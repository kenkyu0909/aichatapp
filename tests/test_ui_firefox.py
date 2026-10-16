"""Firefox UI tests use a temporary app copy, empty SQLite, and fictional data."""
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "test-results"
ERROR_MONITOR = """<script>
window.__runtimeErrors = [];
window.__consoleErrors = [];
window.addEventListener('error', event => window.__runtimeErrors.push(String(event.message || 'script error')));
window.addEventListener('unhandledrejection', event => window.__runtimeErrors.push(String(event.reason || 'unhandled rejection')));
const originalConsoleError = console.error.bind(console);
console.error = (...args) => { window.__consoleErrors.push(args.map(String).join(' ')); originalConsoleError(...args); };
</script>"""


class LocalApp:
    def __init__(self, data_dir: Path, app_dir: Path, log_path: Path):
        self.data_dir = data_dir
        self.app_dir = app_dir
        self.log_path = log_path
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.port = sock.getsockname()[1]
        self.url = f"http://127.0.0.1:{self.port}/"
        self.process = None
        self._prepare_app()

    def _prepare_app(self):
        self.app_dir.mkdir(parents=True, exist_ok=True)
        for name in ("app.py", "app.js", "index.html", "style.css"):
            shutil.copy2(ROOT / name, self.app_dir / name)
        shutil.copytree(ROOT / "prompts", self.app_dir / "prompts", dirs_exist_ok=True)
        shutil.copy2(
            ROOT / "tests" / "firefox_mocked_gemini_server.py",
            self.app_dir / "firefox_mocked_gemini_server.py",
        )
        index_path = self.app_dir / "index.html"
        html = index_path.read_text(encoding="utf-8")
        html = html.replace('<script src="./app.js" defer></script>', ERROR_MONITOR + '\n  <script src="./app.js" defer></script>')
        index_path.write_text(html, encoding="utf-8")

    def start(self, *, mocked_gemini=False, require_movie_answer=False):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["APP_DATA_DIR"] = str(self.data_dir)
        env["MRA_API_DIR"] = str(self.app_dir / "empty-api")
        env.pop("MRA_API_1_KEY", None)
        env.pop("MRA_API_2_KEY", None)
        env.pop("GEMINI_API_KEY", None)
        env.pop("MRA_TEST_REQUIRE_MOVIE_ANSWER", None)
        command = [sys.executable, "-m", "uvicorn", "app:app"]
        if mocked_gemini:
            # The local server sees a fake key only to enter the normal provider
            # path. The test launcher replaces google.genai.Client in-process,
            # so no Gemini SDK client or network request can be created.
            self.mock_calls_path = self.data_dir / "mock-provider-calls.jsonl"
            env["MRA_API_1_KEY"] = "test-only-key-not-a-credential"
            env["MRA_PROVIDER_MIN_INTERVAL_SECONDS"] = "0"
            env["MRA_MAX_PROVIDER_ATTEMPTS_PER_GENERATE"] = "1"
            env["MRA_TEST_GEMINI_CALL_LOG"] = str(self.mock_calls_path)
            if require_movie_answer:
                env["MRA_TEST_REQUIRE_MOVIE_ANSWER"] = "1"
            command = [sys.executable, "firefox_mocked_gemini_server.py"]
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log = self.log_path.open("ab")
        self.process = subprocess.Popen(
            [*command, "--host", "127.0.0.1", "--port", str(self.port)],
            cwd=self.app_dir,
            env=env,
            stdout=self._log,
            stderr=subprocess.STDOUT,
        )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError("local app exited before readiness; see test-results/server.log")
            try:
                with urllib.request.urlopen(self.url + "api/status", timeout=0.5) as response:
                    if response.status == 200:
                        return
            except (OSError, urllib.error.URLError):
                time.sleep(0.2)
        raise TimeoutError("local app did not become ready within 20 seconds")

    def stop(self):
        if self.process and self.process.poll() is None:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(self.process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                self.process.terminate()
            try:
                self.process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if getattr(self, "_log", None):
            self._log.close()


@pytest.fixture
def local_app(tmp_path):
    app = LocalApp(tmp_path / "empty-test-database", tmp_path / "app-copy", ARTIFACTS / "server.log")
    try:
        app.start()
        yield app
    finally:
        app.stop()


@pytest.fixture
def local_app_with_mocked_gemini(tmp_path):
    app = LocalApp(
        tmp_path / "empty-provider-test-database",
        tmp_path / "provider-mocked-app-copy",
        ARTIFACTS / "server-mocked-gemini.log",
    )
    try:
        app.start(mocked_gemini=True)
        yield app
    finally:
        app.stop()


@pytest.fixture
def firefox():
    options = Options()
    options.add_argument("-headless")
    firefox_binary = os.getenv("FIREFOX_BIN")
    if firefox_binary:
        options.binary_location = firefox_binary
    elif os.name == "nt":
        options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    log_path = ARTIFACTS / "geckodriver.log"
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    driver = webdriver.Firefox(options=options, service=Service(log_output=str(log_path)))
    driver.set_window_size(1440, 1100)
    driver.set_page_load_timeout(20)
    driver.implicitly_wait(0.2)
    try:
        yield driver
    finally:
        driver.quit()


def visible_toast(driver, text):
    def matches(browser):
        toast = browser.find_element(By.ID, "toast")
        return text in toast.text if toast.is_displayed() else False
    # Firefox can spend several seconds processing the local API while the page
    # is loaded alongside the rest of the suite; wait for async completion rather
    # than timing out at the toast's normal display duration.
    return WebDriverWait(driver, 15).until(matches)


def modal(driver):
    return driver.find_element(By.ID, "modal")


def add_fictional_contact(driver, name="架空のあおい"):
    driver.find_element(By.ID, "new-contact").click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    fields = modal(driver).find_elements(By.CSS_SELECTOR, "#modal-body input:not([type=file])")
    fields[0].send_keys(name)
    modal(driver).find_elements(By.CSS_SELECTOR, "#modal-body textarea")[0].send_keys(
        "旅行とカフェ巡りが好きです。休日は読書をしています。"
    )
    modal(driver).find_element(By.CSS_SELECTOR, "button.confirm").click()
    WebDriverWait(driver, 8).until(
        lambda browser: browser.execute_script(
            "return Array.from(document.querySelectorAll('.contact-item')).some(item => item.textContent.includes(arguments[0]))",
            name,
        )
    )
    WebDriverWait(driver, 8).until(
        lambda browser: browser.find_element(By.ID, "first-message").is_displayed()
    )


def instrumented_errors(driver):
    return driver.execute_script("return {runtime: window.__runtimeErrors, console: window.__consoleErrors}")


def record_artifact(name: str, driver, extra=None, allow_console_errors=False):
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(ARTIFACTS / f"{name}.png"))
    errors = instrumented_errors(driver)
    sha = os.getenv("GITHUB_SHA")
    dirty = False
    if not sha:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"os": sys.platform, "python": sys.version.split()[0], "browser": "Firefox"},
        "test": name,
        "result": "PASS" if not errors["runtime"] and (not errors["console"] or allow_console_errors) else "FAIL",
        "commit_sha": sha,
        "working_tree_dirty": dirty,
        "runtime_errors": errors["runtime"],
        "console_errors": errors["console"],
        "details": extra or {},
    }
    (ARTIFACTS / f"{name}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return errors


def install_generate_mock(driver):
    # Route only the AI endpoint to a deterministic fabricated response.
    driver.execute_script("""
      window.__generateResponses = [];
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/generate') {
          const payload = JSON.parse(options.body || '{}');
          window.__generateResponses.push(payload);
          return new Response(JSON.stringify({
            recommended: {label:'自然体', text:'そのカフェ、落ち着けそうですね。'},
            alternatives: [
              {label:'質問', text:'ケーキは何を食べたんですか？'},
              {label:'短め', text:'素敵ですね、いい週末ですね。'}
            ], reason:'架空データのUIテスト用モックです。',
            strategy:'相手の話題を一つ拾って、無理のない質問を続けます。', demo:false
          }), {status:200, headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """)


def test_firefox_console_and_core_ui_with_strategy_toggle(local_app, firefox):
    app = local_app
    driver = firefox
    driver.get(app.url)
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text != "")
    assert modal(driver).get_attribute("open") is None
    install_generate_mock(driver)

    driver.find_element(By.CSS_SELECTOR, 'button[data-open="profile"]').click()
    modal(driver).find_elements(By.CSS_SELECTOR, "#modal-body input")[0].send_keys("架空の学生")
    modal(driver).find_element(By.CSS_SELECTOR, "button.confirm").click()
    WebDriverWait(driver, 8).until(
        lambda browser: modal(browser).get_attribute("open") is None
    )
    with urllib.request.urlopen(app.url + "api/profile", timeout=3) as response:
        assert json.load(response)["content"]

    add_fictional_contact(driver)
    search = driver.find_element(By.ID, "search")
    search.send_keys("あおい")
    assert len(driver.find_elements(By.CSS_SELECTOR, ".contact-item")) == 1
    search.clear()
    message_input = driver.find_element(By.ID, "message-input")
    message_input.send_keys("週末は友達とカフェに行きました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)

    driver.find_element(By.CSS_SELECTOR, "article.chat-message.them button").click()
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body textarea").clear()
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body textarea").send_keys(
        "週末は友達と落ち着いたカフェに行きました！"
    )
    modal(driver).find_element(By.CSS_SELECTOR, "button.confirm").click()
    visible_toast(driver, "履歴を更新しました")
    assert driver.find_element(By.CSS_SELECTOR, "article.chat-message.them .bubble").text == "週末は友達と落ち着いたカフェに行きました！"

    message_input.send_keys("削除確認用の架空メッセージ")
    driver.find_element(By.ID, "send-me").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1
    )
    driver.find_element(By.CSS_SELECTOR, "article.chat-message.me button:last-child").click()
    driver.switch_to.alert.accept()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 0
    )
    visible_toast(driver, "メッセージを削除しました")

    policy = driver.find_element(By.ID, "policy")
    assert policy.is_selected()
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert len(driver.find_elements(By.CSS_SELECTOR, ".policy-suggestion")) == 1
    assert driver.execute_script("return window.__generateResponses.at(-1).show_policy") is True

    policy.click()
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert len(driver.find_elements(By.CSS_SELECTOR, ".policy-suggestion")) == 0
    assert driver.execute_script("return window.__generateResponses.at(-1).show_policy") is False

    policy.click()
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert len(driver.find_elements(By.CSS_SELECTOR, ".policy-suggestion")) == 1
    assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == 3
    assert driver.execute_script("return window.__generateResponses.at(-1).show_policy") is True

    message_count = len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message"))
    driver.find_element(By.CSS_SELECTOR, ".candidate button").click()
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == message_count
    if modal(driver).get_attribute("open") is not None:
        driver.find_element(By.ID, "close-modal").click()

    driver.find_element(By.CSS_SELECTOR, 'button[data-open="like"]').click()
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body textarea").send_keys(
        "休日は水族館や美術館に行くことが多いです。旅行も好きです。"
    )
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "#modal .candidate")) == 3)
    driver.find_element(By.ID, "close-modal").click()

    driver.find_element(By.CSS_SELECTOR, 'button[data-open="settings"]').click()
    assert modal(driver).get_attribute("open") is not None
    driver.find_element(By.ID, "close-modal").click()
    driver.refresh()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    assert driver.find_element(By.ID, "current-name").text == "架空のあおい"
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 1
    errors = record_artifact("firefox-core-ui", driver, {"strategy_states": [True, False, True], "candidate_count": 3, "message_delete": True})
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_discards_generation_finished_after_reselecting_same_contact(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text != "")
    add_fictional_contact(driver, "架空のひなた")
    driver.find_element(By.ID, "message-input").send_keys("昨日はカフェに行きました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )
    driver.execute_script("""
      window.__resolveHeldGeneration = null;
      const originalFetch = window.fetch.bind(window);
      window.fetch = (url, options = {}) => {
        if (String(url) === '/api/generate') {
          return new Promise(resolve => {
            window.__resolveHeldGeneration = () => resolve(new Response(JSON.stringify({
              recommended:{label:'古い候補',text:'この候補は再選択後に表示しない！'},
              alternatives:[{label:'別案',text:'この履歴には属さない候補！'}],
              reason:'遅延応答テスト',strategy:'遅延応答',demo:false
            }),{status:200,headers:{'Content-Type':'application/json'}}));
          });
        }
        return originalFetch(url, options);
      };
    """)

    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__resolveHeldGeneration !== null")
    )
    driver.find_element(By.CSS_SELECTOR, ".contact-item.active").click()
    WebDriverWait(driver, 8).until(
        lambda browser: "会話履歴を読み込み中です" not in browser.find_element(By.ID, "messages").text
        and "昨日はカフェに行きました！" in browser.find_element(By.ID, "messages").text
    )
    driver.execute_script("window.__resolveHeldGeneration()")
    WebDriverWait(driver, 5).until(
        lambda browser: browser.find_element(By.ID, "generate").get_attribute("disabled") is None
    )
    assert not driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")
    assert "昨日はカフェに行きました！" in driver.find_element(By.ID, "messages").text
    errors = record_artifact("firefox-discard-stale-generation-after-same-contact-reselect", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_ignores_older_history_load_for_same_contact(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のすみれ")
    driver.find_element(By.ID, "message-input").send_keys("現在の履歴に残る発言！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: "現在の履歴に残る発言！" in browser.find_element(By.ID, "messages").text
    )
    driver.execute_script(r"""
      const originalFetch = window.fetch.bind(window);
      window.__heldHistory = [];
      window.__completedHistoryLoads = 0;
      window.fetch = (url, options = {}) => {
        if (String(url).match(/^\/api\/matches\/\d+\/messages$/)) {
          const index = window.__heldHistory.length;
          return new Promise(resolve => {
            window.__heldHistory.push(() => resolve(
              index === 0
                ? new Response(JSON.stringify([{id:999,role:'them',body:'古い履歴応答！',created_at:'old'}]), {status:200,headers:{'Content-Type':'application/json'}})
                : originalFetch(url, options)
            ));
          }).then(response => { window.__completedHistoryLoads += 1; return response; });
        }
        return originalFetch(url, options);
      };
    """)

    driver.find_element(By.CSS_SELECTOR, ".contact-item.active").click()
    driver.find_element(By.CSS_SELECTOR, ".contact-item.active").click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__heldHistory.length") == 2
    )
    driver.execute_script("window.__heldHistory[1]()")
    WebDriverWait(driver, 8).until(
        lambda browser: "現在の履歴に残る発言！" in browser.find_element(By.ID, "messages").text
        and not browser.find_element(By.ID, "generate").get_attribute("hidden")
    )
    driver.execute_script("window.__heldHistory[0]()")
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__completedHistoryLoads") == 2
    )
    assert "現在の履歴に残る発言！" in driver.find_element(By.ID, "messages").text
    assert "古い履歴応答！" not in driver.find_element(By.ID, "messages").text
    errors = record_artifact("firefox-ignore-older-same-contact-history-load", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_stale_generation_cannot_enable_new_contact_request(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のあおい")
    driver.find_element(By.ID, "message-input").send_keys("昨日はカフェに行きました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )
    add_fictional_contact(driver, "架空のゆず")
    driver.find_element(By.ID, "message-input").send_keys("旅行の話をしました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )
    driver.execute_script("""
      window.__heldGenerations = [];
      const originalFetch = window.fetch.bind(window);
      window.fetch = (url, options = {}) => {
        if (String(url) === '/api/generate') {
          const index = window.__heldGenerations.length;
          return new Promise(resolve => window.__heldGenerations.push(() => resolve(new Response(
            JSON.stringify({
              recommended:{label:'候補'+index,text:'架空の候補'+index+'！'},
              alternatives:[{label:'別案',text:'架空の別候補'+index+'！'}],
              reason:'遅延応答テスト',strategy:'応答順テスト',demo:false
            }),{status:200,headers:{'Content-Type':'application/json'}}
          ))));
        }
        return originalFetch(url, options);
      };
    """)

    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__heldGenerations.length") == 1
    )
    search = driver.find_element(By.ID, "search")
    search.send_keys("あおい")
    driver.find_element(By.CSS_SELECTOR, ".contact-item").click()
    WebDriverWait(driver, 8).until(
        lambda browser: "昨日はカフェに行きました！" in browser.find_element(By.ID, "messages").text
    )
    search.clear()
    search.send_keys("ゆず")
    driver.find_element(By.CSS_SELECTOR, ".contact-item").click()
    WebDriverWait(driver, 8).until(
        lambda browser: "旅行の話をしました！" in browser.find_element(By.ID, "messages").text
    )
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__heldGenerations.length") == 2
    )
    driver.execute_script("window.__heldGenerations[0]()")
    time.sleep(0.2)
    assert driver.find_element(By.ID, "generate").get_attribute("disabled") is not None
    assert not driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")
    driver.execute_script("window.__heldGenerations[1]()")
    WebDriverWait(driver, 8).until(
        lambda browser: browser.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")
    )
    assert driver.find_element(By.CSS_SELECTOR, ".candidate-text").text == "架空の候補1！"
    errors = record_artifact("firefox-stale-generation-preserves-new-request-lock", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_handles_server_stop_and_restart_without_losing_input(local_app, firefox):
    app = local_app
    driver = firefox
    driver.get(app.url)
    add_fictional_contact(driver, "架空のゆき")
    driver.find_element(By.ID, "message-input").send_keys("架空の相手への未保存メッセージ")
    app.stop()

    driver.find_element(By.ID, "send-them").click()
    visible_toast(driver, "ローカルサーバーと通信できません")
    assert driver.find_element(By.ID, "message-input").get_attribute("value") == "架空の相手への未保存メッセージ"
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 0

    driver.find_element(By.CSS_SELECTOR, 'button[data-open="profile"]').click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    profile_dialog = modal(driver)
    profile_field = profile_dialog.find_elements(By.CSS_SELECTOR, "#modal-body input")[0]
    profile_field.send_keys("再起動後も保持する架空プロフィール")
    if driver.find_element(By.ID, "toast").is_displayed():
        driver.execute_script("document.getElementById('toast').hidden = true")
    profile_dialog.find_element(By.CSS_SELECTOR, "button.confirm").click()
    visible_toast(driver, "ローカルサーバーと通信できません")
    assert profile_dialog.get_attribute("open") is not None
    assert profile_field.get_attribute("value").endswith("再起動後も保持する架空プロフィール")
    driver.find_element(By.ID, "close-modal").click()

    driver.execute_script("document.getElementById('toast').hidden = true")
    driver.find_element(By.ID, "first-message").click()
    visible_toast(driver, "ローカルサーバーと通信できません")
    assert driver.find_element(By.ID, "first-message").is_enabled()
    assert not driver.find_element(By.ID, "suggestion-list").is_displayed()
    assert instrumented_errors(driver)["runtime"] == []

    driver.find_element(By.ID, "new-contact").click()
    add_dialog = modal(driver)
    name_field = add_dialog.find_elements(By.CSS_SELECTOR, "#modal-body input:not([type=file])")[0]
    name_field.send_keys("再送できる架空の相手")
    add_dialog.find_elements(By.CSS_SELECTOR, "#modal-body textarea")[0].send_keys("架空プロフィール")
    if driver.find_element(By.ID, "toast").is_displayed():
        driver.execute_script("document.getElementById('toast').hidden = true")
    add_dialog.find_element(By.CSS_SELECTOR, "button.confirm").click()
    visible_toast(driver, "ローカルサーバーと通信できません")
    assert add_dialog.get_attribute("open") is not None
    assert name_field.get_attribute("value").endswith("再送できる架空の相手")

    try:
        app.start()
    except Exception:
        app.stop()
        raise
    add_dialog.find_element(By.CSS_SELECTOR, "button.confirm").click()
    visible_toast(driver, "相手の情報を保存しました")
    driver.find_element(By.CSS_SELECTOR, 'button[data-open="profile"]').click()
    modal(driver).find_element(By.CSS_SELECTOR, "button.confirm").click()
    WebDriverWait(driver, 8).until(
        lambda browser: modal(browser).get_attribute("open") is None
    )
    next(item for item in driver.find_elements(By.CSS_SELECTOR, ".contact-item") if "架空のゆき" in item.text).click()
    driver.find_element(By.ID, "send-them").click()
    visible_toast(driver, "相手の発言を履歴に登録しました")
    driver.refresh()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".contact-item")) == 2)
    original = next(item for item in driver.find_elements(By.CSS_SELECTOR, ".contact-item") if "架空のゆき" in item.text)
    original.click()
    assert driver.find_element(By.ID, "current-name").text == "架空のゆき"
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 1
    errors = record_artifact("firefox-server-stop-restart", driver, {"offline_actions": 4}, allow_console_errors=True)
    assert errors["runtime"] == []


def test_firefox_first_message_and_temporary_profile_questions(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のあおい")
    install_generate_mock(driver)
    driver.execute_script("""
      window.__generateResponses = [];
      window.__generateResults = [];
      window.__profileWrites = [];
      window.__allowSkipFallback = false;
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/profile' && options.method === 'PUT') window.__profileWrites.push(options.body);
        if (String(url) === '/api/generate') {
          const payload = JSON.parse(options.body || '{}');
          window.__generateResponses.push(payload);
          const result = payload.skipped_user_info && window.__allowSkipFallback ? {
            recommended:{label:'安全な話題',text:'プロフィールのカフェ巡りが気になりました！最近行ってよかったお店はありますか？'},
            alternatives:[{label:'短め',text:'カフェ巡りいいですね！'}, {label:'別案',text:'旅行もお好きなんですね！'}],
            reason:'本人の未確認情報を使わず、相手のプロフィールだけに触れています'
          } : payload.skipped_user_info ? {
            needs_user_info:false,skipped_user_info:true,generation_blocked:true,
            recommended:null,alternatives:[],
            blocking_reason:'プロフィールが未登録のため初回メッセージを作れません'
          } : !payload.user_answers?.length ? {
            needs_user_info: true,
            user_questions: [{question:'映画は好きですか？', purpose:'本人の好みを事実として返信へ反映するため'}],
            user_info_reason:'本人プロフィールに映画の情報がありません'
          } : {
            recommended:{label:'自然体',text:'映画好きです！洋画をよく観ます☺️'},
            alternatives:[{label:'短め',text:'洋画をよく観ます！'}, {label:'話題を広げる',text:'洋画いいですね！最近何か観ましたか？'}],
            reason:'本人が回答した内容だけを使っています',
            strategy:'記載情報: 相手から映画の話題。根拠: 本人が洋画好きと回答。次の行動: 好きなジャンルを尋ねる。',
            conversation_stage:'Stage 3', invite_decision:'consider_invite',
            decision_reason:'会話を始めたばかりです', next_action:'映画の話題を続ける'
          };
          window.__generateResults.push(result);
          return new Response(JSON.stringify(result), {status:200, headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """)

    first_button = driver.find_element(By.ID, "first-message")
    assert first_button.is_displayed()
    assert not driver.find_element(By.ID, "generate").is_displayed()
    first_button.click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".user-info-question")) == 1)
    assert "返信候補とも別に表示します" in driver.find_element(By.ID, "suggestion-list").text
    assert "一時的に使います" in driver.find_element(By.ID, "suggestion-list").text
    assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == 0
    driver.find_element(By.ID, "skip-user-info").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".user-info-terminal")) == 1)
    assert not driver.find_elements(By.CSS_SELECTOR, ".user-info-question")
    assert driver.find_element(By.CSS_SELECTOR, ".suggestion-heading").text == "✦ 初回メッセージは作成できませんでした"
    assert driver.execute_script("return window.__generateResponses.at(-1).skipped_user_info") is True
    assert "プロフィールが未登録" in driver.find_element(By.CSS_SELECTOR, ".user-info-terminal").text
    assert driver.execute_script("return window.__generateResults.at(-1).generation_blocked") is True
    assert not driver.execute_script("return window.__generateResponses.at(-1).user_answers")
    driver.find_element(By.ID, "first-message").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".user-info-question")) == 1)
    driver.execute_script("window.__allowSkipFallback=true")
    driver.find_element(By.ID, "skip-user-info").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert not driver.find_elements(By.CSS_SELECTOR, ".user-info-question")
    assert driver.find_element(By.CSS_SELECTOR, ".suggestion-heading").text == "✦ 初回メッセージ候補"
    driver.find_element(By.ID, "first-message").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".user-info-question")) == 1)
    add_fictional_contact(driver, "架空のゆき")
    assert not driver.find_elements(By.CSS_SELECTOR, ".user-info-panel")
    next(item for item in driver.find_elements(By.CSS_SELECTOR, ".contact-item") if "架空のあおい" in item.text).click()
    driver.find_element(By.ID, "first-message").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".user-info-question")) == 1)
    driver.find_element(By.CSS_SELECTOR, ".user-info-answer").send_keys("映画は好きで洋画をよく観る")
    driver.find_element(By.ID, "resume-generation").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    sent = driver.find_element(By.CSS_SELECTOR, ".candidate-text").text
    assert "洋画をよく観ます" in sent
    assert driver.find_element(By.CSS_SELECTOR, ".suggestion-heading").text == "✦ 初回メッセージ候補"
    assert driver.execute_script("return window.__generateResponses.at(-1).response_version") == 2
    assert driver.execute_script("return window.__generateResponses.at(-1).user_answers[0].answer") == "映画は好きで洋画をよく観る"
    assert driver.execute_script("return window.__generateResponses.at(-1).match_id") == driver.execute_script("return window.__generateResponses.at(-2).match_id")
    assert driver.execute_script("return window.__profileWrites") == []
    strategy = driver.find_element(By.CSS_SELECTOR, ".policy-suggestion").text
    assert "Stage 3 — 食事などへの誘いを検討する段階" in strategy
    assert "食事などへの誘いを検討" in strategy
    assert "consider_invite" not in strategy
    assert "映画の話題" in strategy

    message_count = len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message"))
    driver.find_element(By.CSS_SELECTOR, ".candidate button:last-child").click()
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == message_count
    if modal(driver).get_attribute("open") is not None:
        driver.find_element(By.ID, "close-modal").click()
    assert driver.find_element(By.ID, "first-message").is_displayed()
    driver.find_element(By.CSS_SELECTOR, ".candidate button:nth-child(2)").click()
    modal(driver).find_element(By.CSS_SELECTOR, "button.confirm").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1)
    assert not driver.find_element(By.ID, "first-message").is_displayed()
    assert driver.find_element(By.ID, "generate").is_displayed()
    assert driver.find_element(By.CSS_SELECTOR, "article.chat-message.me .bubble").text == sent
    errors = record_artifact("firefox-first-message-user-info", driver, {"user_info_answers_persisted": False})
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_optional_user_question_keeps_candidates_and_only_regenerates(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のあおい")
    driver.find_element(By.ID, "message-input").send_keys("最近小説を読みました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    install_generate_mock(driver)
    driver.execute_script("""
      window.__generateResponses = [];
      window.__profileWrites = [];
      window.__messageWrites = [];
      window.__failNextAnswer = true;
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/profile' && options.method === 'PUT') window.__profileWrites.push(options.body);
        if (String(url).includes('/messages') && options.method === 'POST') window.__messageWrites.push(options.body);
        if (String(url) === '/api/generate') {
          const payload = JSON.parse(options.body || '{}');
          window.__generateResponses.push(payload);
          if (!window.__firstMatchId) window.__firstMatchId = payload.match_id;
          if (payload.user_answers?.length && window.__failNextAnswer) {
            window.__failNextAnswer = false;
            return new Response(JSON.stringify({detail:'一時的な再生成失敗'}), {status:503, headers:{'Content-Type':'application/json'}});
          }
          const callNumber = window.__generateResponses.length;
          const optionalQuestion = payload.match_id !== window.__firstMatchId ? {
            question:'普段どんなジャンルの本を読みますか？',
            scope_key:'reading.genre',
            purpose:'本人の読書傾向に触れる返信を作るため'
          } : payload.user_answers?.length ? {
            question:'このところ読んだ作品で印象に残ったものはありますか？',
            scope_key:'reading.recent',
            purpose:'具体的な本の話へ広げるため'
          } : callNumber === 1 ? {
            question:'普段どんなジャンルの本を読みますか？',
            scope_key:'reading.genre',
            purpose:'本人の読書傾向に触れる返信を作るため'
          } : callNumber === 2 ? {
            question:'本は普段何系を読むことが多いですか？',
            scope_key:'reading.genre',
            purpose:'本人の読書傾向に触れる返信を作るため'
          } : callNumber === 3 ? {
            question:'最近読んだ本の中で印象に残ったものはありますか？',
            scope_key:'reading.recent',
            purpose:'具体的な本の話へ広げるため'
          } : {
            question:'好きな作家はいますか？',
            scope_key:'reading.author',
            purpose:'新しい話題へ広げるため'
          };
          const result = {
            recommended:{label:'自然な返信',text:'本の話いいですね！最近読んでよかった作品はありますか？'},
            alternatives:[
              {label:'話題を広げる',text:'読書いいですね！どんな本が好きですか？'},
              {label:'短め',text:'本の話いいですね！'}
            ],
            optional_user_questions: [optionalQuestion]
          };
          return new Response(JSON.stringify(result), {status:200, headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """);
    driver.execute_script("window.__messageWrites = []");

    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".optional-user-question")) == 1)
    assert len(driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")) == 3
    assert "候補はこのまま使えます" in driver.find_element(By.CSS_SELECTOR, ".optional-user-question").text
    assert "プロフィールには保存しません" in driver.find_element(By.CSS_SELECTOR, ".optional-user-question").text
    assert "送信しません" in driver.find_element(By.CSS_SELECTOR, ".optional-user-question").text
    candidates_before_skip = [el.text for el in driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate-text")]
    driver.find_element(By.ID, "skip-optional-user-question").click()
    assert not driver.find_elements(By.CSS_SELECTOR, ".optional-user-question")
    assert [el.text for el in driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate-text")] == candidates_before_skip
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 0

    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.execute_script("return window.__generateResponses") or []) == 2)
    assert not driver.find_elements(By.CSS_SELECTOR, ".optional-user-question")
    assert len(driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")) == 3

    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".optional-user-question")) == 1)
    driver.find_element(By.ID, "optional-user-answer").send_keys("ミステリーをよく読みます")
    driver.find_element(By.ID, "answer-and-regenerate-optional").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.execute_script("return window.__generateResponses") or []) == 4)
    WebDriverWait(driver, 5).until(lambda browser: "一時的な再生成失敗" in browser.find_element(By.ID, "toast").text)
    assert len(driver.find_elements(By.CSS_SELECTOR, ".optional-user-question")) == 1
    assert driver.find_element(By.ID, "optional-user-answer").get_attribute("value") == "ミステリーをよく読みます"
    assert driver.execute_script("return window.__profileWrites") == []
    assert driver.execute_script("return window.__messageWrites") == []

    driver.find_element(By.ID, "answer-and-regenerate-optional").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.execute_script("return window.__generateResponses") or []) == 5)
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".optional-user-question")) == 0)
    payload = driver.execute_script("return window.__generateResponses.at(-1)")
    assert payload["user_answers"] == [{
        "question":"最近読んだ本の中で印象に残ったものはありますか？",
        "answer":"ミステリーをよく読みます"
    }]
    assert len(driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")) == 3
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.execute_script("return window.__generateResponses") or []) == 6)
    assert len(driver.find_elements(By.CSS_SELECTOR, ".optional-user-question")) == 1
    assert "好きな作家はいますか？" in driver.find_element(By.CSS_SELECTOR, ".optional-user-question").text
    assert len(driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")) == 3
    assert driver.execute_script("return window.__profileWrites") == []
    assert driver.execute_script("return window.__messageWrites") == []
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 0

    add_fictional_contact(driver, "架空のみお")
    driver.find_element(By.ID, "message-input").send_keys("最近小説を読みました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    driver.execute_script("window.__messageWrites = []")
    next(item for item in driver.find_elements(By.CSS_SELECTOR, ".contact-item") if "架空のみお" in item.text).click()
    WebDriverWait(driver, 5).until(lambda browser: "架空のみお" in browser.find_element(By.ID, "current-name").text)
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.execute_script("return window.__generateResponses") or []) == 7)
    assert "普段どんなジャンルの本を読みますか？" in driver.find_element(By.CSS_SELECTOR, ".optional-user-question").text
    next(item for item in driver.find_elements(By.CSS_SELECTOR, ".contact-item") if "架空のあおい" in item.text).click()
    WebDriverWait(driver, 5).until(lambda browser: "架空のあおい" in browser.find_element(By.ID, "current-name").text)
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(lambda browser: len(browser.execute_script("return window.__generateResponses") or []) == 8)
    assert "好きな作家はいますか？" in driver.find_element(By.CSS_SELECTOR, ".optional-user-question").text
    assert len(driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")) == 3
    assert driver.execute_script("return window.__profileWrites") == []
    assert driver.execute_script("return window.__messageWrites") == []
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 0
    errors = record_artifact("firefox-optional-user-question", driver, {"answers_persisted":False,"auto_sent":False})
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_disables_conversation_actions_until_history_is_loaded(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空の読み込み確認")
    driver.execute_script("""
      const originalFetch = window.fetch.bind(window);
      window.__holdHistory = true;
      window.fetch = async (url, options = {}) => {
        if (window.__holdHistory && String(url).match(/^\\/api\\/matches\\/\\d+\\/messages$/)) {
          window.__holdHistory = false;
          return new Promise(resolve => {
            window.__resumeHistory = async () => resolve(await originalFetch(url, options));
          });
        }
        return originalFetch(url, options);
      };
    """)

    driver.find_element(By.CSS_SELECTOR, ".contact-item").click()
    WebDriverWait(driver, 5).until(lambda browser: browser.execute_script("return !!window.__resumeHistory"))
    assert "会話履歴を読み込み中です" in driver.find_element(By.ID, "messages").text
    assert not driver.find_element(By.ID, "first-message").is_displayed()
    assert driver.find_element(By.ID, "message-input").get_attribute("disabled") is not None
    assert driver.find_element(By.ID, "send-them").get_attribute("disabled") is not None

    driver.execute_script("window.__resumeHistory()")
    WebDriverWait(driver, 5).until(lambda browser: browser.find_element(By.ID, "first-message").is_displayed())
    assert driver.find_element(By.ID, "message-input").get_attribute("disabled") is None
    errors = record_artifact("firefox-history-loading-controls", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_first_to_reply_copy_manual_record_and_history_flow(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のあおい")
    first_text = "はじめまして！\nマッチできてうれしいです☺️\nカフェ巡り好きなんですね！"
    reply_text = "えーいいですね！\n最近行ったお店で印象に残ったところありますか？"
    driver.execute_script("""
      window.__generatePayloads = [];
      window.__copiedText = undefined;
      Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText: async text => {window.__copiedText=text;}}});
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/generate') {
          const payload = JSON.parse(options.body || '{}');
          window.__generatePayloads.push(payload);
          const text = payload.mode === 'first' ? arguments[0] : arguments[1];
          return new Response(JSON.stringify({
            recommended:{label:'自然な返信',text},
            alternatives:[
              {label:'別の切り口',text:'カフェ巡りいいですね！'},
              {label:'短い返信',text:'それ楽しそうです！'}
            ], reason:'Firefoxの架空データUI検証用モックです', demo:false
          }), {status:200,headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """, first_text, reply_text)

    driver.find_element(By.ID, "first-message").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert driver.execute_script("return window.__generatePayloads.at(-1).mode") == "first"
    assert driver.find_element(By.CSS_SELECTOR, ".candidate-text").text == first_text
    driver.find_element(By.CSS_SELECTOR, ".candidate button:first-child").click()
    WebDriverWait(driver, 5).until(lambda browser: browser.execute_script("return window.__copiedText !== undefined"))
    assert driver.execute_script("return window.__copiedText") == first_text
    assert driver.find_elements(By.CSS_SELECTOR, "article.chat-message.me") == []

    driver.find_element(By.CSS_SELECTOR, ".candidate button:nth-child(2)").click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1)
    assert driver.find_element(By.CSS_SELECTOR, "article.chat-message.me .bubble").text == first_text

    driver.find_element(By.ID, "message-input").send_keys("休日は友達とカフェに行ってきました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert driver.execute_script("return window.__generatePayloads.at(-1).mode") == "reply"
    assert driver.find_element(By.CSS_SELECTOR, ".candidate-text").text == reply_text
    driver.find_element(By.CSS_SELECTOR, ".candidate button:first-child").click()
    WebDriverWait(driver, 5).until(lambda browser: browser.execute_script("return window.__copiedText === arguments[0]", reply_text))
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1

    driver.find_element(By.CSS_SELECTOR, ".candidate button:nth-child(2)").click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 2)
    driver.find_element(By.ID, "history-button").click()
    history_text = modal(driver).text
    assert first_text in history_text
    assert reply_text in history_text
    driver.find_element(By.ID, "close-modal").click()
    driver.refresh()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 3)
    restored_messages = []
    for message in driver.find_elements(By.CSS_SELECTOR, "article.chat-message"):
        role = "me" if "me" in message.get_attribute("class").split() else "them"
        restored_messages.append((role, message.find_element(By.CSS_SELECTOR, ".bubble").text))
    assert restored_messages == [
        ("me", first_text),
        ("them", "休日は友達とカフェに行ってきました！"),
        ("me", reply_text),
    ]
    errors = record_artifact("firefox-first-reply-send-history", driver, {
        "modes": ["first", "reply"],
        "copied_without_recording": True,
        "manually_recorded_messages": 2,
        "history_survived_reload": True,
    })
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_uses_real_fastapi_generate_route_with_only_gemini_sdk_mocked(
    local_app_with_mocked_gemini, firefox
):
    """Exercise browser -> FastAPI -> Gemini SDK seam without external traffic."""
    local_app = local_app_with_mocked_gemini
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のあおい")

    incoming = "休日は友達とカフェに行ってきました！"
    driver.find_element(By.ID, "message-input").send_keys(incoming)
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )
    driver.execute_script("""
      window.__copiedText = undefined;
      window.__actualGenerateResponses = [];
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: {writeText: async text => {window.__copiedText = text;}}
      });
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        const response = await originalFetch(url, options);
        if (String(url) === '/api/generate') {
          window.__actualGenerateResponses.push(await response.clone().json());
        }
        return response;
      };
    """)

    # No fetch interception is installed: this click reaches the temporary,
    # loopback-only FastAPI process and its normal /api/generate implementation.
    driver.find_element(By.ID, "generate").click()
    expected = "えーいいですね！\nどんなカフェだったんですか？"
    WebDriverWait(driver, 15).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3
    )
    first_candidate = driver.find_elements(By.CSS_SELECTOR, ".candidate")[0]
    assert first_candidate.find_element(By.CSS_SELECTOR, ".candidate-text").text == expected
    assert not driver.find_elements(By.CSS_SELECTOR, ".demo-warning")
    actual_response = driver.execute_script("return window.__actualGenerateResponses.at(-1)")
    assert actual_response["demo"] is False
    assert actual_response["api_alias"] == "API1"
    assert actual_response["model"] == "gemini-3.5-flash-lite"

    # The real browser response and in-process SDK replacement together prove
    # that the route entered its provider path, not app.py's fixed demo path.
    # The placeholder credential is never recorded.
    WebDriverWait(driver, 5).until(lambda _: local_app.mock_calls_path.exists())
    calls = [
        json.loads(line)
        for line in local_app.mock_calls_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(calls) == 1
    assert calls[0]["model"] == "gemini-3.5-flash-lite"
    assert calls[0]["input_contains_incoming_message"] is True
    assert calls[0]["system_instruction_present"] is True

    first_candidate.find_element(By.CSS_SELECTOR, ".candidate-actions button:first-child").click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__copiedText !== undefined")
    )
    assert driver.execute_script("return window.__copiedText") == expected
    assert driver.find_elements(By.CSS_SELECTOR, "article.chat-message.me") == []

    record_button = first_candidate.find_elements(By.CSS_SELECTOR, ".candidate-actions button")[1]
    record_button.click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1
    )
    assert driver.find_element(By.CSS_SELECTOR, "article.chat-message.me .bubble").text == expected

    driver.refresh()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 2
    )
    restored = [
        ("me" if "me" in item.get_attribute("class").split() else "them",
         item.find_element(By.CSS_SELECTOR, ".bubble").text)
        for item in driver.find_elements(By.CSS_SELECTOR, "article.chat-message")
    ]
    assert restored == [("them", incoming), ("me", expected)]
    errors = record_artifact(
        "firefox-real-generate-route-sdk-mocked",
        driver,
        {
            "route": "/api/generate",
            "provider": "google.genai.Client replaced inside test server process",
            "provider_calls": len(calls),
            "external_gemini_calls": 0,
            "api_alias": actual_response["api_alias"],
            "model": actual_response["model"],
            "copied_without_recording": True,
            "manual_record_and_reload_persisted": True,
            "binding": "127.0.0.1",
        },
    )
    assert errors["runtime"] == []
    assert errors["console"] == []



def test_firefox_real_generate_route_covers_first_followup_and_like_modes(
    local_app_with_mocked_gemini, firefox
):
    """Exercise each remaining generation mode through FastAPI with no provider traffic."""
    app = local_app_with_mocked_gemini
    driver = firefox
    driver.get(app.url)
    add_fictional_contact(driver, "架空のりお")

    with urllib.request.urlopen(app.url + "api/matches", timeout=3) as response:
        matches = json.load(response)
    match_id = next(item["id"] for item in matches if item["name"] == "架空のりお")

    def saved_history():
        with urllib.request.urlopen(app.url + f"api/matches/{match_id}/messages", timeout=3) as response:
            return json.load(response)

    driver.execute_script("""
      window.__modeGenerateResponses = [];
      window.__copiedText = undefined;
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: {writeText: async text => {window.__copiedText = text;}}
      });
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        const response = await originalFetch(url, options);
        if (String(url) === '/api/generate') {
          window.__modeGenerateResponses.push(await response.clone().json());
        }
        return response;
      };
    """)

    # First mode is available with an empty conversation. Generation alone
    # must not create a self message in SQLite.
    assert driver.find_element(By.ID, "first-message").is_displayed()
    assert saved_history() == []
    driver.find_element(By.ID, "first-message").click()
    WebDriverWait(driver, 15).until(
        lambda browser: browser.execute_script("return window.__modeGenerateResponses.length") == 1
        and browser.find_elements(By.CSS_SELECTOR, ".candidate")
    )
    first_response = driver.execute_script("return window.__modeGenerateResponses.at(-1)")
    assert first_response["demo"] is False
    assert first_response["conversation_stage"] == "Stage 1"
    assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == first_response["available_candidate_count"]
    assert first_response["available_candidate_count"] < first_response["requested_candidate_count"]
    assert "不足分を不自然な候補で補っていません" in first_response["candidate_notice"]
    visible_candidate_notice = driver.find_element(
        By.CSS_SELECTOR, "#suggestion-list .user-info-terminal"
    ).text
    assert "安全確認後に表示できる候補は" in visible_candidate_notice
    assert "不足分を不自然な候補で補っていません" in visible_candidate_notice
    assert first_response["recommended"]["text"].startswith("はじめまして！")
    assert saved_history() == []

    first_card = driver.find_elements(By.CSS_SELECTOR, ".candidate")[0]
    first_record = first_card.find_elements(By.CSS_SELECTOR, ".candidate-actions button")[1]
    first_record.click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(lambda _: len(saved_history()) == 1)
    first_history = saved_history()
    assert first_history[0]["role"] == "me"
    assert first_history[0]["body"] == first_response["recommended"]["text"]

    # Follow-up is generated from actual stored self history. It remains only
    # a suggestion until its explicit manual-record action is confirmed.
    WebDriverWait(driver, 8).until(
        lambda browser: browser.find_element(By.ID, "follow-up").is_displayed()
    )
    followup_button = driver.find_element(By.ID, "follow-up")
    followup_button.click()
    WebDriverWait(driver, 15).until(
        lambda browser: browser.execute_script("return window.__modeGenerateResponses.length") == 2
        and browser.find_elements(By.CSS_SELECTOR, ".candidate")
    )
    followup_response = driver.execute_script("return window.__modeGenerateResponses.at(-1)")
    assert followup_response["demo"] is False
    assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == followup_response["available_candidate_count"]
    assert "追いメッセージ" in driver.find_element(By.CSS_SELECTOR, "#suggestion-list .suggestion-heading").text
    assert saved_history() == first_history
    followup_card = driver.find_elements(By.CSS_SELECTOR, ".candidate")[0]
    followup_buttons = followup_card.find_elements(By.CSS_SELECTOR, ".candidate-actions button")
    assert len(followup_buttons) == 2
    followup_buttons[0].click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__copiedText !== undefined")
    )
    assert driver.execute_script("return window.__copiedText") == followup_response["recommended"]["text"]
    assert saved_history() == first_history
    followup_buttons[1].click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(lambda _: len(saved_history()) == 2)
    followup_history = saved_history()
    assert followup_history[-1]["role"] == "me"
    assert followup_history[-1]["body"] == followup_response["recommended"]["text"]

    # Like mode is pre-match: its independent modal permits copying but never
    # offers a record action or changes the selected match's sent history.
    driver.find_element(By.CSS_SELECTOR, 'button[data-open="like"]').click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    like_modal = modal(driver)
    like_modal.find_element(By.CSS_SELECTOR, "#modal-body input").send_keys("架空のりお")
    like_modal.find_element(By.CSS_SELECTOR, "#modal-body textarea").send_keys(
        "カフェ巡りと美術館が好きです。"
    )
    like_modal.find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 15).until(
        lambda browser: browser.execute_script("return window.__modeGenerateResponses.length") == 3
        and browser.find_elements(By.CSS_SELECTOR, "#modal .candidate")
    )
    like_response = driver.execute_script("return window.__modeGenerateResponses.at(-1)")
    assert like_response["demo"] is False
    assert len(like_modal.find_elements(By.CSS_SELECTOR, ".candidate")) == like_response["available_candidate_count"]
    assert not like_modal.find_elements(By.CSS_SELECTOR, ".candidate-actions button:nth-child(2)")
    like_modal.find_element(By.CSS_SELECTOR, ".candidate-actions button:first-child").click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__copiedText !== undefined")
    )
    assert driver.execute_script("return window.__copiedText") == like_response["recommended"]["text"]
    assert saved_history() == followup_history
    driver.find_element(By.ID, "close-modal").click()
    driver.refresh()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 2
    )
    assert saved_history() == followup_history

    WebDriverWait(driver, 5).until(lambda _: app.mock_calls_path.exists())
    provider_calls = [
        json.loads(line)
        for line in app.mock_calls_path.read_text(encoding="utf-8").splitlines()
    ]
    assert [call["mode"] for call in provider_calls] == ["first", "followup", "like"]
    assert all(call["system_instruction_present"] for call in provider_calls)
    assert all(call["model"] == "gemini-3.5-flash-lite" for call in provider_calls)
    assert all("test-only-key-not-a-credential" not in json.dumps(call) for call in provider_calls)

    errors = record_artifact(
        "firefox-real-generate-first-followup-like-sdk-mocked",
        driver,
        {
            "routes": ["/api/generate"] * 3,
            "modes": ["first", "followup", "like"],
            "provider_calls": len(provider_calls),
            "external_gemini_calls": 0,
            "first_and_followup_manual_recorded": True,
            "like_copy_did_not_change_history": True,
            "binding": "127.0.0.1",
        },
    )
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_user_info_roundtrip_uses_real_route_and_temporary_answer(tmp_path, firefox):
    app = LocalApp(
        tmp_path / "user-info-test-database",
        tmp_path / "user-info-app-copy",
        ARTIFACTS / "server-user-info-mocked-gemini.log",
    )
    try:
        app.start(mocked_gemini=True, require_movie_answer=True)
        driver = firefox
        driver.get(app.url)
        add_fictional_contact(driver, "架空のあかり")
        with urllib.request.urlopen(app.url + "api/profile", timeout=3) as response:
            profile_before = json.load(response)

        driver.find_element(By.ID, "message-input").send_keys("映画好きですか？")
        driver.find_element(By.ID, "send-them").click()
        WebDriverWait(driver, 8).until(
            lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
        )
        with urllib.request.urlopen(app.url + "api/matches", timeout=3) as response:
            matches = json.load(response)
        match_id = next(item["id"] for item in matches if item["name"] == "架空のあかり")

        driver.execute_script("""
          window.__realRouteResponses = [];
          window.__copiedText = undefined;
          Object.defineProperty(navigator, 'clipboard', {
            configurable: true,
            value: {writeText: async text => {window.__copiedText = text;}}
          });
          const originalFetch = window.fetch.bind(window);
          window.fetch = async (url, options = {}) => {
            const response = await originalFetch(url, options);
            if (String(url) === '/api/generate') {
              window.__realRouteResponses.push(await response.clone().json());
            }
            return response;
          };
        """)

        driver.find_element(By.ID, "generate").click()
        WebDriverWait(driver, 8).until(
            lambda browser: browser.find_elements(By.CSS_SELECTOR, ".user-info-question")
        )
        first_response = driver.execute_script("return window.__realRouteResponses.at(-1)")
        assert first_response["needs_user_info"] is True
        assert first_response["recommended"] is None
        assert first_response["alternatives"] == []
        assert "映画" in first_response["user_questions"][0]["question"]
        assert not driver.find_elements(By.CSS_SELECTOR, ".candidate")
        assert not app.mock_calls_path.exists(), "本人確認前にGemini provider mockが呼ばれた"

        driver.find_element(By.CSS_SELECTOR, ".user-info-answer").send_keys(
            "映画は好きで洋画をよく観ます"
        )
        driver.find_element(By.ID, "resume-generation").click()
        WebDriverWait(driver, 12).until(
            lambda browser: browser.execute_script("return window.__realRouteResponses.length") == 2
            and browser.find_elements(By.CSS_SELECTOR, ".candidate")
        )
        generated = driver.execute_script("return window.__realRouteResponses.at(-1)")
        assert generated["demo"] is False
        assert generated["recommended"]["text"] == "映画好きで洋画をよく観ます！"
        assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == generated["available_candidate_count"]
        assert all(
            "映画" in candidate.text or "洋画" in candidate.text
            for candidate in driver.find_elements(By.CSS_SELECTOR, ".candidate-text")
        )

        with urllib.request.urlopen(app.url + f"api/matches/{match_id}/messages", timeout=3) as response:
            history = json.load(response)
        assert [(item["role"], item["body"]) for item in history] == [("them", "映画好きですか？")]
        with urllib.request.urlopen(app.url + "api/profile", timeout=3) as response:
            assert json.load(response) == profile_before

        driver.find_element(By.CSS_SELECTOR, ".candidate-actions button:first-child").click()
        WebDriverWait(driver, 5).until(
            lambda browser: browser.execute_script("return window.__copiedText !== undefined")
        )
        assert driver.execute_script("return window.__copiedText") == generated["recommended"]["text"]
        with urllib.request.urlopen(app.url + f"api/matches/{match_id}/messages", timeout=3) as response:
            assert json.load(response) == history

        provider_calls = [
            json.loads(line)
            for line in app.mock_calls_path.read_text(encoding="utf-8").splitlines()
        ]
        assert len(provider_calls) == 1
        assert provider_calls[0]["mode"] == "reply"
        assert provider_calls[0]["user_answer_count"] == 1
        assert provider_calls[0]["user_answer_matches_expected"] is True
        assert provider_calls[0]["model"] == "gemini-3.5-flash-lite"
        errors = record_artifact(
            "firefox-real-generate-user-info-roundtrip-sdk-mocked",
            driver,
            {
                "routes": ["/api/generate"] * 2,
                "provider_calls": 1,
                "provider_calls_before_user_answer": 0,
                "answer_saved_to_profile": False,
                "copy_created_sent_message": False,
                "external_gemini_calls": 0,
                "binding": "127.0.0.1",
            },
        )
        assert errors["runtime"] == []
        assert errors["console"] == []
    finally:
        app.stop()


def test_firefox_required_clarification_keeps_answers_across_multiple_questions(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のゆい")
    driver.find_element(By.ID, "message-input").send_keys("最近どんな本を読みますか？")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )

    driver.execute_script("""
      window.__clarificationRequests = [];
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) !== '/api/generate') return originalFetch(url, options);
        const payload = JSON.parse(options.body || '{}');
        window.__clarificationRequests.push(payload);
        const index = window.__clarificationRequests.length;
        const body = index === 1
          ? {needs_user_info:true,recommended:null,alternatives:[],user_questions:[{question:'普段どんなジャンルの本を読みますか？'}]}
          : index === 2
            ? {needs_user_info:true,recommended:null,alternatives:[],user_questions:[{question:'最近読んだ本はありますか？'}]}
            : {needs_user_info:false,recommended:{label:'自然な案',text:'ミステリーを読むことが多いです！'},alternatives:[{label:'別案',text:'最近はミステリーが多いです！'},{label:'短め',text:'ミステリーが好きです！'}],reason:'モック応答',available_candidate_count:3};
        return new Response(JSON.stringify(body), {status:200,headers:{'Content-Type':'application/json'}});
      };
    """)

    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_elements(By.CSS_SELECTOR, ".user-info-question"))
    driver.find_element(By.CSS_SELECTOR, ".user-info-answer").send_keys("ミステリーが好きです")
    driver.find_element(By.ID, "resume-generation").click()
    WebDriverWait(driver, 8).until(
        lambda browser: browser.execute_script("return window.__clarificationRequests.length") == 2
        and browser.find_elements(By.CSS_SELECTOR, ".user-info-question")
    )
    driver.find_element(By.CSS_SELECTOR, ".user-info-answer").send_keys("最近は架空の『青い栞』を読みました")
    driver.find_element(By.ID, "resume-generation").click()
    WebDriverWait(driver, 8).until(
        lambda browser: browser.execute_script("return window.__clarificationRequests.length") == 3
        and browser.find_elements(By.CSS_SELECTOR, ".candidate")
    )
    requests = driver.execute_script("return window.__clarificationRequests")
    assert requests[0].get("user_answers", []) == []
    assert requests[1]["user_answers"] == [
        {"question":"普段どんなジャンルの本を読みますか？", "answer":"ミステリーが好きです"}
    ]
    assert requests[2]["user_answers"] == [
        {"question":"普段どんなジャンルの本を読みますか？", "answer":"ミステリーが好きです"},
        {"question":"最近読んだ本はありますか？", "answer":"最近は架空の『青い栞』を読みました"},
    ]
    assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == 3
    assert "user-info-panel" not in driver.find_element(By.ID, "suggestion-list").get_attribute("innerHTML")
    errors = record_artifact(
        "firefox-multistep-user-info-answers-retained",
        driver,
        {"clarification_rounds": 2, "answers_accumulated_for_same_generation": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_preserves_candidate_line_breaks_in_display_copy_and_saved_history(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のあおい")
    message_input = driver.find_element(By.ID, "message-input")
    message_input.send_keys("休日は友達とカフェに行くことが多いです！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )
    expected = "えーそうなんですね！\nカフェ巡り楽しそうです😊\n最近行ってよかったお店ありますか？"
    driver.execute_script("""
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/generate' || String(url) === '/api/generate') {
          return new Response(JSON.stringify({
            recommended:{label:'自然体',text:arguments[0]},
            alternatives:[
              {label:'短め',text:'カフェ巡りいいですね！'},
              {label:'別の切り口',text:'最近行ったお店で印象に残ったところありますか？'}
            ],reason:'相手の発言に合わせています'
          }), {status:200,headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """, expected)
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    first = driver.find_element(By.CSS_SELECTOR, ".candidate-text")
    assert driver.execute_script("return arguments[0].textContent", first) == expected
    assert driver.execute_script("return getComputedStyle(arguments[0]).whiteSpace", first) == "pre-wrap"
    driver.execute_script("Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText: async text => {window.__copiedText=text;}}});")
    driver.find_element(By.CSS_SELECTOR, ".candidate button").click()
    WebDriverWait(driver, 5).until(lambda browser: browser.execute_script("return window.__copiedText !== undefined"))
    assert driver.execute_script("return window.__copiedText") == expected
    assert driver.find_elements(By.CSS_SELECTOR, "article.chat-message.me") == []
    driver.find_element(By.CSS_SELECTOR, ".candidate button:last-child").click()
    textarea = driver.find_element(By.CSS_SELECTOR, "#modal-body textarea")
    assert textarea.get_attribute("value") == expected
    driver.find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1
    )
    stored = driver.find_element(By.CSS_SELECTOR, "article.chat-message.me .bubble")
    assert driver.execute_script("return arguments[0].textContent", stored).strip() == expected
    driver.refresh()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1
    )
    stored_after_reload = driver.find_element(By.CSS_SELECTOR, "article.chat-message.me .bubble")
    assert driver.execute_script("return arguments[0].textContent", stored_after_reload).strip() == expected


def test_firefox_distinguishes_invalid_candidate_and_rate_limit_errors(local_app, firefox):
    app = local_app
    driver = firefox
    driver.get(app.url)
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text != "")
    add_fictional_contact(driver)
    driver.find_element(By.ID, "message-input").send_keys("今日はカフェに行きました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    driver.execute_script("""
      const originalFetch = window.fetch.bind(window);
      window.__mockErrorCode = 'invalid_response';
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/generate') {
          const body = {error_code:window.__mockErrorCode, detail:'secret-safe detail'};
          return new Response(JSON.stringify(body), {status:502, headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """)
    driver.find_element(By.ID, "generate").click()
    visible_toast(driver, "生成した候補が返信ルールに合わなかったため表示できませんでした")
    assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == 0

    driver.execute_script("window.__mockErrorCode='all_models_rate_limited'")
    driver.find_element(By.ID, "generate").click()
    visible_toast(driver, "Geminiの利用制限に達しました")
    assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == 0

    driver.execute_script("window.__mockErrorCode='request_attempt_limit'")
    driver.find_element(By.ID, "generate").click()
    visible_toast(driver, "生成の安全試行上限に達したため停止しました")
    assert len(driver.find_elements(By.CSS_SELECTOR, ".candidate")) == 0
    errors = record_artifact("firefox-generation-error-categories", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_keeps_safe_candidate_visible_with_shortage_notice(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空の候補確認")
    driver.find_element(By.ID, "message-input").send_keys("休日は友達とカフェに行くことが多いです！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )
    driver.execute_script("""
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/generate') {
          return new Response(JSON.stringify({
            recommended:{label:'安全な案',text:'そのカフェ気になります！'},
            alternatives:[], reason:'架空データのUI検証', strategy:'会話を続ける',
            demo:false, generation_blocked:false,
            requested_candidate_count:3, available_candidate_count:1,
            candidate_notice:'安全確認後に表示できる候補は1案です（指定は3案）。不足分を不自然な候補で補っていません。'
          }), {status:200,headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """)

    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 1)
    assert "表示できる候補は1案" in driver.find_element(By.CSS_SELECTOR, ".user-info-terminal").text
    assert driver.find_element(By.CSS_SELECTOR, ".candidate-text").text == "そのカフェ気になります！"
    errors = record_artifact(
        "firefox-safe-candidate-shortage",
        driver,
        {"requested_candidate_count": 3, "available_candidate_count": 1, "safe_candidate_retained": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []


def _conversation_loaded(driver, expected_name, expected_message):
    try:
        name = driver.find_element(By.ID, "current-name").text
        messages = [
            message.text
            for message in driver.find_elements(
                By.CSS_SELECTOR, "article.chat-message.them .bubble"
            )
        ]
    except StaleElementReferenceException:
        return False
    return name == expected_name and messages == [expected_message]


def test_firefox_stale_candidate_cannot_be_recorded_after_switching_match(local_app, firefox):
    app = local_app
    driver = firefox
    driver.get(local_app.url)
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text != "")
    install_generate_mock(driver)

    add_fictional_contact(driver, "架空のあおい")
    driver.find_element(By.ID, "message-input").send_keys("休日は友達とカフェに行きました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )

    add_fictional_contact(driver, "架空のゆき")
    driver.find_element(By.ID, "message-input").send_keys("最近は美術館に行きました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )

    contact_a = next(
        item for item in driver.find_elements(By.CSS_SELECTOR, ".contact-item")
        if "架空のあおい" in item.text
    )
    contact_a.click()
    WebDriverWait(driver, 8).until(
        lambda browser: _conversation_loaded(
            browser, "架空のあおい", "休日は友達とカフェに行きました！"
        )
    )
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 1

    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    driver.find_element(By.CSS_SELECTOR, ".candidate button:nth-child(2)").click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    assert "実際に送信した文章を記録" in modal(driver).find_element(By.ID, "modal-title").text

    # The native dialog blocks pointer clicks on the contact list. Dispatch the
    # same contact button handler to model a selection change while the stale
    # candidate confirmation remains open.
    driver.execute_script("""
      const item = Array.from(document.querySelectorAll('.contact-item'))
        .find(button => button.textContent.includes('架空のゆき'));
      item.click();
    """)
    WebDriverWait(driver, 8).until(
        lambda browser: _conversation_loaded(
            browser, "架空のゆき", "最近は美術館に行きました！"
        )
    )

    modal(driver).find_element(By.CSS_SELECTOR, "button.confirm").click()
    visible_toast(driver, "相手が変わっています。もう一度確認してください")
    assert modal(driver).get_attribute("open") is not None
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 0

    driver.find_element(By.ID, "close-modal").click()
    assert driver.find_element(By.ID, "current-name").text == "架空のゆき"
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 1
    assert driver.find_element(By.CSS_SELECTOR, "article.chat-message.them .bubble").text == "最近は美術館に行きました！"

    contact_a = next(
        item for item in driver.find_elements(By.CSS_SELECTOR, ".contact-item")
        if "架空のあおい" in item.text
    )
    contact_a.click()
    WebDriverWait(driver, 8).until(
        lambda browser: _conversation_loaded(
            browser, "架空のあおい", "休日は友達とカフェに行きました！"
        )
    )
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 1
    assert driver.find_element(By.CSS_SELECTOR, "article.chat-message.them .bubble").text == "休日は友達とカフェに行きました！"

    with urllib.request.urlopen(app.url + "api/matches", timeout=3) as response:
        matches = json.load(response)
    match_ids = {item["name"]: item["id"] for item in matches}
    assert set(match_ids) >= {"架空のあおい", "架空のゆき"}
    for name, expected in (
        ("架空のあおい", "休日は友達とカフェに行きました！"),
        ("架空のゆき", "最近は美術館に行きました！"),
    ):
        with urllib.request.urlopen(
            app.url + f"api/matches/{match_ids[name]}/messages", timeout=3
        ) as response:
            messages = json.load(response)
        assert [(message["role"], message["body"]) for message in messages] == [("them", expected)]

    errors = record_artifact(
        "firefox-stale-candidate-recording",
        driver,
        {"record_attempt_rejected": True, "old_and_new_histories_unchanged": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_followup_copy_and_manual_record_preserve_multiline_history(local_app, firefox):
    """Follow-up candidates stay unsent until explicitly recorded and retain newlines."""
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のさくら")
    with urllib.request.urlopen(local_app.url + "api/matches", timeout=3) as response:
        selected_match_id = next(
            item["id"] for item in json.load(response) if item["name"] == "架空のさくら"
        )

    incoming = "最近は仕事が忙しくて少し疲れています"
    already_sent = "無理しすぎないでくださいね"
    followup = "落ち着いたらゆっくり休めるといいですね\n返信は気にしないでください😊"
    driver.find_element(By.ID, "message-input").send_keys(incoming)
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1
    )
    driver.find_element(By.ID, "message-input").send_keys(already_sent)
    driver.find_element(By.ID, "send-me").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1
    )
    assert [
        "me" if "me" in item.get_attribute("class").split() else "them"
        for item in driver.find_elements(By.CSS_SELECTOR, "article.chat-message")
    ] == ["them", "me"]

    driver.execute_script("""
      window.__generationPayloads = [];
      window.__copiedText = undefined;
      Object.defineProperty(navigator, 'clipboard', {
        configurable:true,
        value:{writeText: async text => {window.__copiedText=text;}}
      });
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/generate') {
          const payload = JSON.parse(options.body || '{}');
          window.__generationPayloads.push(payload);
          return new Response(JSON.stringify({
            recommended:{label:'やさしい案',text:arguments[0]},
            alternatives:[
              {label:'短め',text:'返信は大丈夫です！'},
              {label:'別の案',text:'無理せず過ごしてくださいね'}
            ],
            reason:'相手を急かさない架空データのモックです',
            demo:false
          }), {status:200,headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """, followup)

    driver.find_element(By.ID, "follow-up").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert driver.execute_script("return window.__generationPayloads.at(-1).mode") == "followup"
    assert driver.execute_script("return window.__generationPayloads.at(-1).match_id") == selected_match_id
    candidate = driver.find_element(By.CSS_SELECTOR, ".candidate-text")
    assert driver.execute_script("return arguments[0].textContent", candidate) == followup
    assert driver.execute_script("return getComputedStyle(arguments[0]).whiteSpace", candidate) == "pre-wrap"

    initial_history = [
        ("them", incoming),
        ("me", already_sent),
    ]
    def visible_history(browser):
        return [
            ("me" if "me" in item.get_attribute("class").split() else "them",
             item.find_element(By.CSS_SELECTOR, ".bubble").get_attribute("textContent").strip())
            for item in browser.find_elements(By.CSS_SELECTOR, "article.chat-message")
        ]
    def saved_history():
        with urllib.request.urlopen(
            local_app.url + f"api/matches/{selected_match_id}/messages", timeout=3
        ) as response:
            return [(item["role"], item["body"]) for item in json.load(response)]

    assert visible_history(driver) == initial_history
    assert saved_history() == initial_history

    driver.find_element(By.CSS_SELECTOR, ".candidate button:first-child").click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__copiedText !== undefined")
    )
    assert driver.execute_script("return window.__copiedText") == followup
    assert visible_history(driver) == initial_history
    assert saved_history() == initial_history

    driver.find_element(By.CSS_SELECTOR, ".candidate button:nth-child(2)").click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    assert "実際に送信した文章を記録" in modal(driver).find_element(By.ID, "modal-title").text
    textarea = modal(driver).find_element(By.CSS_SELECTOR, "#modal-body textarea")
    assert textarea.get_attribute("value") == followup
    edited_followup = "落ち着いたらゆっくり休んでくださいね\n返信は気にしないでください😊"
    textarea.clear()
    textarea.send_keys(edited_followup)
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 2)
    expected_history = initial_history + [("me", edited_followup)]
    assert visible_history(driver) == expected_history
    assert saved_history() == expected_history

    errors = record_artifact(
        "firefox-followup-copy-record-before-reload",
        driver,
        {"mode": "followup", "copy_preserved_history": True, "multiline_saved": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []

    driver.refresh()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 3)
    assert visible_history(driver) == expected_history
    assert saved_history() == expected_history
    errors = record_artifact(
        "firefox-followup-history-after-reload",
        driver,
        {"mode": "followup", "multiline_saved_and_restored": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_like_candidate_can_be_copied_without_creating_match_history(local_app, firefox):
    """Pre-match like candidates can be copied but never recorded as sent messages."""
    app = local_app
    driver = firefox
    driver.get(app.url)
    add_fictional_contact(driver, "架空のりお")

    with urllib.request.urlopen(app.url + "api/matches", timeout=3) as response:
        matches = json.load(response)
    match_id = next(item["id"] for item in matches if item["name"] == "架空のりお")

    def saved_history():
        with urllib.request.urlopen(app.url + f"api/matches/{match_id}/messages", timeout=3) as response:
            return json.load(response)

    assert saved_history() == []
    like_text = "プロフィールの美術館巡りが気になりました！\n最近行ってよかった展示はありますか？"
    driver.execute_script("""
      window.__likePayloads = [];
      window.__copiedText = undefined;
      Object.defineProperty(navigator, 'clipboard', {
        configurable:true,
        value:{writeText: async text => {window.__copiedText=text;}}
      });
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/generate') {
          const payload = JSON.parse(options.body || '{}');
          window.__likePayloads.push(payload);
          return new Response(JSON.stringify({
            recommended:{label:'自然な初回のきっかけ',text:arguments[0]},
            alternatives:[
              {label:'短め',text:'美術館いいですね！'},
              {label:'別の話題',text:'旅行もお好きなんですね！'}
            ],
            reason:'プロフィールの情報だけを使った架空データのモックです',
            demo:false
          }), {status:200,headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """, like_text)

    driver.find_element(By.CSS_SELECTOR, 'button[data-open="like"]').click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    body = modal(driver)
    body.find_element(By.CSS_SELECTOR, "#modal-body input").send_keys("架空のりお")
    body.find_element(By.CSS_SELECTOR, "#modal-body textarea").send_keys(
        "休日は美術館や水族館に行きます。旅行も好きです。"
    )
    body.find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "#modal .candidate")) == 3
    )
    assert driver.execute_script("return window.__likePayloads.at(-1).mode") == "like"
    assert driver.execute_script("return window.__likePayloads.at(-1).match_id") is None
    assert driver.execute_script("return window.__likePayloads.at(-1).name") == "架空のりお"
    assert driver.execute_script("return window.__likePayloads.at(-1).count") == 3
    assert body.find_element(By.CSS_SELECTOR, "#modal .candidate-text").get_attribute("textContent") == like_text
    assert len(body.find_elements(By.CSS_SELECTOR, "#modal .candidate button")) == 3
    assert not body.find_elements(By.CSS_SELECTOR, "#modal .candidate button:nth-child(2)")

    body.find_element(By.CSS_SELECTOR, "#modal .candidate button:first-child").click()
    WebDriverWait(driver, 5).until(
        lambda browser: browser.execute_script("return window.__copiedText !== undefined")
    )
    assert driver.execute_script("return window.__copiedText") == like_text
    WebDriverWait(driver, 5).until(
        lambda browser: "送信済み履歴には追加していません" in browser.find_element(By.ID, "toast").text
    )
    assert saved_history() == []

    driver.find_element(By.ID, "close-modal").click()
    assert saved_history() == []
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 0
    errors = record_artifact(
        "firefox-like-copy-no-history-before-reload",
        driver,
        {"mode": "like", "copied_candidate": True, "conversation_history_unchanged": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []

    driver.refresh()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text == "架空のりお")
    assert len(driver.find_elements(By.CSS_SELECTOR, "article.chat-message")) == 0
    assert saved_history() == []
    errors = record_artifact(
        "firefox-like-copy-no-history-after-reload",
        driver,
        {"mode": "like", "history_still_empty": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_saved_profile_is_available_during_first_and_reply_generation(local_app, firefox):
    """A UI-saved profile persists and can be read at first/reply request time."""
    app = local_app
    driver = firefox
    driver.get(app.url)
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text != "")

    driver.find_element(By.CSS_SELECTOR, 'button[data-open="profile"]').click()
    profile_dialog = modal(driver)
    inputs = profile_dialog.find_elements(By.CSS_SELECTOR, "#modal-body input")
    input_values = [
        "架空のひなた", "28", "東京都", "デザイナー", "読書とカフェ巡り", "落ち着いた性格", "短く自然な口調"
    ]
    assert len(inputs) >= len(input_values)
    for field, value in zip(inputs, input_values):
        field.send_keys(value)
    textareas = profile_dialog.find_elements(By.CSS_SELECTOR, "#modal-body textarea")
    assert len(textareas) == 3
    textareas[0].send_keys("自然な会話を大切にしたいです")
    textareas[1].send_keys("休日は本屋やカフェへ行きます")
    textareas[2].send_keys("急な誘いは避けたい")
    profile_json = json.dumps({
        "name": "架空のひなた",
        "age": "28",
        "area": "東京都",
        "job": "デザイナー",
        "hobbies": "読書とカフェ巡り",
        "personality": "落ち着いた性格",
        "style": "短く自然な口調",
        "goal": "自然な会話を大切にしたいです",
        "memo": "休日は本屋やカフェへ行きます",
    }, ensure_ascii=False, separators=(",", ":"))
    profile_dialog.find_element(By.CSS_SELECTOR, "button.confirm").click()
    # This test verifies persistence and availability during generation. The
    # toast disappears after four seconds and can be missed if Firefox is
    # briefly busy on a shared CI runner, so wait on the durable modal state.
    WebDriverWait(driver, 8).until(
        lambda browser: browser.find_element(By.ID, "modal").get_attribute("open") is None
    )

    with urllib.request.urlopen(app.url + "api/profile", timeout=3) as response:
        saved_profile = json.load(response)
    assert saved_profile == {"content": profile_json, "avoid": "急な誘いは避けたい"}

    add_fictional_contact(driver, "架空のなな")
    first_text = "はじめまして！マッチできてうれしいです\n読書とカフェ巡りがお好きなんですね！"
    reply_text = "カフェ巡りいいですね！\n最近行ってよかったお店はありますか？"
    driver.execute_script("""
      window.__generationObservations = [];
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        if (String(url) === '/api/generate') {
          const payload = JSON.parse(options.body || '{}');
          const profileResponse = await originalFetch('/api/profile');
          const profile = await profileResponse.json();
          window.__generationObservations.push({payload, profile});
          const candidateText = payload.mode === 'first' ? arguments[0] : arguments[1];
          return new Response(JSON.stringify({
            recommended:{label:'自然な案',text:candidateText},
            alternatives:[
              {label:'短め',text:'プロフィールのお話が気になりました！'},
              {label:'別の質問',text:'休日はどんなお店に行くことが多いですか？'}
            ],
            reason:'架空プロフィールを利用したUIテスト用モックです',demo:false
          }), {status:200,headers:{'Content-Type':'application/json'}});
        }
        return originalFetch(url, options);
      };
    """, first_text, reply_text)

    driver.find_element(By.ID, "first-message").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert driver.execute_script("return window.__generationObservations.at(-1).payload.mode") == "first"
    assert driver.execute_script("return window.__generationObservations.at(-1).payload.match_id") is not None
    assert driver.execute_script("return window.__generationObservations.at(-1).profile") == saved_profile
    assert driver.find_element(By.CSS_SELECTOR, ".candidate-text").get_attribute("textContent") == first_text

    driver.find_element(By.CSS_SELECTOR, ".candidate button:nth-child(2)").click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    modal(driver).find_element(By.CSS_SELECTOR, "#modal-body button.confirm").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.me")) == 1)
    driver.find_element(By.ID, "message-input").send_keys("休日は友達とカフェに行ってきました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".candidate")) == 3)
    assert driver.execute_script("return window.__generationObservations.at(-1).payload.mode") == "reply"
    assert driver.execute_script("return window.__generationObservations.at(-1).payload.match_id") is not None
    assert driver.execute_script("return window.__generationObservations.at(-1).profile") == saved_profile
    assert driver.find_element(By.CSS_SELECTOR, ".candidate-text").get_attribute("textContent") == reply_text

    errors = record_artifact(
        "firefox-profile-generation-before-reload",
        driver,
        {"profile_saved_via_ui": True, "modes": ["first", "reply"], "profile_endpoint_read_at_request": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []


    driver.refresh()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text == "架空のなな")
    driver.find_element(By.CSS_SELECTOR, 'button[data-open="profile"]').click()
    restored_dialog = modal(driver)
    restored_inputs = restored_dialog.find_elements(By.CSS_SELECTOR, "#modal-body input")
    assert [field.get_attribute("value") for field in restored_inputs[:7]] == input_values
    restored_textareas = restored_dialog.find_elements(By.CSS_SELECTOR, "#modal-body textarea")
    assert [field.get_attribute("value") for field in restored_textareas] == [
        "自然な会話を大切にしたいです",
        "休日は本屋やカフェへ行きます",
        "急な誘いは避けたい",
    ]
    with urllib.request.urlopen(app.url + "api/profile", timeout=3) as response:
        assert json.load(response) == saved_profile
    errors = record_artifact(
        "firefox-profile-retained-after-reload",
        driver,
        {"profile_retained_after_reload": True},
    )
    assert errors["runtime"] == []
    assert errors["console"] == []

def test_firefox_profile_edit_preserves_extension_fields_and_array_types(local_app, firefox):
    driver = firefox
    profile = {
        "name": "架空の本人",
        "age": "28",
        "hobbies": ["読書", "カフェ巡り"],
        "food": {"favorite": "カレー", "avoid": ["辛すぎる料理"]},
        "availability": ["日曜昼"],
        "confirmed_facts": [{"value": "ミステリーが好き", "source": "user"}],
    }
    with urllib.request.urlopen(
        urllib.request.Request(
            local_app.url + "api/profile",
            data=json.dumps({"content": json.dumps(profile, ensure_ascii=False), "avoid": "急な誘い"}).encode(),
            headers={"Content-Type": "application/json"},
            method="PUT",
        ),
        timeout=3,
    ):
        pass

    driver.get(local_app.url)
    WebDriverWait(driver, 8).until(
        lambda browser: "UI" not in browser.find_element(By.CSS_SELECTOR, ".version").text
    )
    driver.find_element(By.CSS_SELECTOR, 'button[data-open="profile"]').click()
    WebDriverWait(driver, 5).until(lambda browser: modal(browser).get_attribute("open") is not None)
    profile_dialog = modal(driver)
    profile_dialog.find_element(By.CSS_SELECTOR, "button.confirm").click()
    WebDriverWait(driver, 5).until(lambda browser: profile_dialog.get_attribute("open") is None)
    with urllib.request.urlopen(local_app.url + "api/profile", timeout=3) as response:
        saved = json.load(response)
    assert json.loads(saved["content"]) == profile
    errors = record_artifact("firefox-profile-extension-fields-roundtrip", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_message_drafts_are_isolated_per_contact(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空A")
    driver.find_element(By.ID, "message-input").send_keys("Aだけの下書き")
    add_fictional_contact(driver, "架空B")
    assert driver.find_element(By.ID, "message-input").get_attribute("value") == ""
    driver.find_element(By.ID, "message-input").send_keys("Bだけの下書き")
    driver.find_element(By.CSS_SELECTOR, ".contact-item:not(.active)").click()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text == "架空A")
    assert driver.find_element(By.ID, "message-input").get_attribute("value") == "Aだけの下書き"
    driver.find_element(By.CSS_SELECTOR, ".contact-item:not(.active)").click()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text == "架空B")
    assert driver.find_element(By.ID, "message-input").get_attribute("value") == "Bだけの下書き"
    errors = record_artifact("firefox-contact-scoped-drafts", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_successful_message_clears_only_its_submitted_draft_after_contact_switch(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "送信中の架空A")
    add_fictional_contact(driver, "架空B")
    driver.find_element(By.CSS_SELECTOR, ".contact-item:not(.active)").click()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text == "送信中の架空A")
    driver.find_element(By.ID, "message-input").send_keys("送信中のAメッセージ")
    driver.execute_script("""
      window.__messagePostCount = 0;
      window.__resolveMessagePost = null;
      window.__messagePostCompleted = false;
      const originalFetch = window.fetch.bind(window);
      window.fetch = (url, options = {}) => {
        if (String(url).endsWith('/messages') && options.method === 'POST') {
          window.__messagePostCount += 1;
          return new Promise(resolve => {
            window.__resolveMessagePost = async () => {
              const response = await originalFetch(url, options);
              window.__messagePostCompleted = true;
              resolve(response);
            };
          });
        }
        return originalFetch(url, options);
      };
    """)
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 5).until(lambda browser: browser.execute_script("return window.__messagePostCount === 1"))
    driver.find_element(By.CSS_SELECTOR, ".contact-item:not(.active)").click()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text == "架空B")
    driver.find_element(By.ID, "message-input").send_keys("Bの未送信下書き")
    driver.execute_script("window.__resolveMessagePost()")
    WebDriverWait(driver, 8).until(lambda browser: browser.execute_script("return window.__messagePostCompleted"))
    driver.find_element(By.CSS_SELECTOR, ".contact-item:not(.active)").click()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text == "送信中の架空A")
    WebDriverWait(driver, 8).until(lambda browser: "送信中のAメッセージ" in browser.find_element(By.ID, "messages").text)
    assert driver.find_element(By.ID, "message-input").get_attribute("value") == ""
    driver.find_element(By.CSS_SELECTOR, ".contact-item:not(.active)").click()
    WebDriverWait(driver, 8).until(lambda browser: browser.find_element(By.ID, "current-name").text == "架空B")
    assert driver.find_element(By.ID, "message-input").get_attribute("value") == "Bの未送信下書き"
    errors = record_artifact("firefox-sent-draft-cleared-after-contact-switch", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_double_click_does_not_submit_duplicate_messages(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "二重送信防止の架空人物")
    driver.find_element(By.ID, "message-input").send_keys("一度だけ保存する発言")
    driver.execute_script("""
      window.__messagePostCount = 0;
      window.__resolveMessagePosts = [];
      const originalFetch = window.fetch.bind(window);
      window.fetch = (url, options = {}) => {
        if (String(url).endsWith('/messages') && options.method === 'POST') {
          window.__messagePostCount += 1;
          return new Promise(resolve => window.__resolveMessagePosts.push(async () => resolve(await originalFetch(url, options))));
        }
        return originalFetch(url, options);
      };
    """)
    send = driver.find_element(By.ID, "send-them")
    send.click()
    send.click()
    time.sleep(0.3)
    assert driver.execute_script("return window.__messagePostCount") == 1
    driver.execute_script("window.__resolveMessagePosts[0]()")
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    assert "一度だけ保存する発言" in driver.find_element(By.ID, "messages").text
    errors = record_artifact("firefox-double-click-does-not-duplicate-message", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_newer_generation_wins_across_modes_for_same_contact(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のひなた")
    driver.find_element(By.ID, "message-input").send_keys("昨日はカフェに行きました！")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    driver.execute_script("""
      window.__heldModes = [];
      const originalFetch = window.fetch.bind(window);
      window.fetch = (url, options = {}) => {
        if (String(url) === '/api/generate') {
          const payload = JSON.parse(options.body);
          return new Promise(resolve => window.__heldModes.push(() => resolve(new Response(JSON.stringify({
            recommended:{label:payload.mode,text:payload.mode === 'reply' ? '古い返信候補！' : '新しい追いメッセージ候補！'},
            alternatives:[],reason:'競合テスト',demo:false
          }),{status:200,headers:{'Content-Type':'application/json'}}))));
        }
        return originalFetch(url, options);
      };
    """)
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(lambda browser: browser.execute_script("return window.__heldModes.length") == 1)
    driver.find_element(By.ID, "follow-up").click()
    WebDriverWait(driver, 5).until(lambda browser: browser.execute_script("return window.__heldModes.length") == 2)
    driver.execute_script("window.__heldModes[1]()")
    WebDriverWait(driver, 5).until(lambda browser: "新しい追いメッセージ候補！" in browser.find_element(By.ID, "suggestion-list").text)
    driver.execute_script("window.__heldModes[0]()")
    time.sleep(0.3)
    assert "新しい追いメッセージ候補！" in driver.find_element(By.ID, "suggestion-list").text
    assert "古い返信候補！" not in driver.find_element(By.ID, "suggestion-list").text
    errors = record_artifact("firefox-generation-latest-request-wins", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []


def test_firefox_message_change_invalidates_generation_for_old_history(local_app, firefox):
    driver = firefox
    driver.get(local_app.url)
    add_fictional_contact(driver, "架空のすみれ")
    driver.find_element(By.ID, "message-input").send_keys("最初の会話内容")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 1)
    driver.execute_script("""
      window.__resolveOldHistoryGeneration = null;
      const originalFetch = window.fetch.bind(window);
      window.fetch = (url, options = {}) => String(url) === '/api/generate'
        ? new Promise(resolve => window.__resolveOldHistoryGeneration = () => resolve(new Response(JSON.stringify({
            recommended:{label:'古い履歴の候補',text:'古い会話に基づく候補！'},alternatives:[],reason:'履歴競合',demo:false
          }),{status:200,headers:{'Content-Type':'application/json'}})))
        : originalFetch(url, options);
    """)
    driver.find_element(By.ID, "generate").click()
    WebDriverWait(driver, 5).until(lambda browser: browser.execute_script("return window.__resolveOldHistoryGeneration !== null"))
    driver.find_element(By.ID, "message-input").send_keys("その後に届いた新しい発言")
    driver.find_element(By.ID, "send-them").click()
    WebDriverWait(driver, 8).until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "article.chat-message.them")) == 2)
    driver.execute_script("window.__resolveOldHistoryGeneration()")
    time.sleep(0.3)
    assert "その後に届いた新しい発言" in driver.find_element(By.ID, "messages").text
    assert not driver.find_elements(By.CSS_SELECTOR, "#suggestion-list .candidate")
    errors = record_artifact("firefox-generation-invalidated-by-history-change", driver)
    assert errors["runtime"] == []
    assert errors["console"] == []

