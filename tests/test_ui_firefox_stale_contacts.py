"""Firefox UI test: contacts without messages for 2 days are hidden by default.

The list hides anyone whose last message is older than 2 days (contacts with no
messages at all stay visible because they were just added). A toggle button in
the sidebar switches between "hide stale" and "show everyone".
"""
import json
import sqlite3
import urllib.request

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from test_ui_firefox import add_fictional_contact, firefox, local_app  # noqa: F401


def contact_names(browser):
    return {
        item.find_element(By.CSS_SELECTOR, "strong").text
        for item in browser.find_elements(By.CSS_SELECTOR, ".contact-item")
    }


def test_firefox_hides_contacts_without_messages_for_two_days(local_app, firefox):  # noqa: F811
    app = local_app
    driver = firefox
    driver.get(app.url)
    WebDriverWait(driver, 8).until(lambda b: b.find_element(By.ID, "current-name").text != "")

    add_fictional_contact(driver, "架空のゆき")
    add_fictional_contact(driver, "架空のあおい")

    base = app.url + "api"
    with urllib.request.urlopen(base + "/matches", timeout=3) as response:
        ids = {m["name"]: m["id"] for m in json.load(response)}
    for name in ("架空のゆき", "架空のあおい"):
        payload = json.dumps({"role": "them", "body": name + "からのテスト"}).encode()
        request = urllib.request.Request(
            base + f"/matches/{ids[name]}/messages",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(request, timeout=3).read()

    # 「ゆき」の最後のメッセージだけを2日より前に書き換える。
    with sqlite3.connect(app.data_dir / "app.sqlite3") as connection:
        connection.execute(
            "UPDATE messages SET created_at='2020-01-01 00:00:00' WHERE match_id=?",
            (ids["架空のゆき"],),
        )
        connection.commit()

    driver.refresh()
    WebDriverWait(driver, 8).until(lambda b: b.find_element(By.ID, "toggle-stale").is_displayed())

    # 既定では2日以上やり取りのない「ゆき」は隠れ、「あおい」だけが一覧に残る。
    WebDriverWait(driver, 8).until(lambda b: "架空のあおい" in contact_names(b))
    assert "架空のゆき" not in contact_names(driver), contact_names(driver)
    toggle = driver.find_element(By.ID, "toggle-stale")
    assert "2日以上を表示" in toggle.text, toggle.text

    # 「表示」ボタンで全員表示に切り替わる。
    toggle.click()
    WebDriverWait(driver, 8).until(lambda b: "架空のゆき" in contact_names(b))
    assert "架空のあおい" in contact_names(driver)
    assert "2日以上を非表示" in driver.find_element(By.ID, "toggle-stale").text

    # もう一度押すと再び非表示に戻る（トグル）。
    driver.find_element(By.ID, "toggle-stale").click()
    WebDriverWait(driver, 8).until(lambda b: "架空のゆき" not in contact_names(b))
