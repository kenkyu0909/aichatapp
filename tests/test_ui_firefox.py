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
        index_path = self.app_dir / "index.html"
        html = index_path.read_text(encoding="utf-8")
        html = html.replace('<script src="./app.js" defer></script>', ERROR_MONITOR + '\n  <script src="./app.js" defer></script>')
        index_path.write_text(html, encoding="utf-8")

    def start(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["APP_DATA_DIR"] = str(self.data_dir)
        env["MRA_API_DIR"] = str(self.app_dir / "empty-api")
        env.pop("MRA_API_1_KEY", None)
        env.pop("MRA_API_2_KEY", None)
        env.pop("GEMINI_API_KEY", None)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log = self.log_path.open("ab")
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(self.port)],
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
    return WebDriverWait(driver, 8).until(matches)


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
        lambda browser: any(name in item.text for item in browser.find_elements(By.CSS_SELECTOR, ".contact-item"))
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
    visible_toast(driver, "自分のプロフィールを保存しました")

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
    visible_toast(driver, "自分のプロフィールを保存しました")
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
            conversation_stage:'Stage 2', invite_decision:'まだ誘わない',
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
    assert "Stage 2" in strategy and "まだ誘わない" in strategy and "映画の話題" in strategy

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
