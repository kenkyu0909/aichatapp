"""One-shot live Gemini smoke test using fictional conversation data only.

Requires GEMINI_API_KEY from GitHub Actions secret. Makes at most two
generate requests, does not print inputs, outputs, or credentials.
"""
import os
import tempfile
from fastapi.testclient import TestClient

assert os.getenv("GEMINI_API_KEY"), "Gemini test key is not configured."

with tempfile.TemporaryDirectory(prefix="fictional-matching-smoke-") as directory:
    os.environ["APP_DATA_DIR"] = directory
    from app import app

    with TestClient(app) as client:
        profile = client.put("/api/profile", json={
            "content": "架空の人物。20代、カフェと読書が好き。短く自然で丁寧な日本語を使う。",
            "avoid": "自分の経験を勝手に作らない",
        })
        assert profile.status_code == 200

        match = client.post("/api/matches", json={
            "name": "架空の人物・あおい",
            "description": "散歩や喫茶店巡りが好き。最近は小説をよく読む。",
        })
        assert match.status_code == 201
        match_id = match.json()["id"]
        incoming = client.post(f"/api/matches/{match_id}/messages", json={
            "role": "them",
            "body": "先週、気になっていた喫茶店に行きました！",
        })
        assert incoming.status_code == 201

        cases = (
            ("reply", {"mode": "reply", "match_id": match_id, "count": 3,
                       "tone": "敬語", "direction": "自然に会話を広げる"}),
            ("like", {"mode": "like", "name": "架空の人物・ゆい",
                      "description": "休日は水族館と読書を楽しんでいます。", "count": 3}),
        )
        for label, payload in cases:
            response = client.post("/api/generate", json=payload)
            if response.status_code != 200:
                # Backend already maps SDK errors to safe, redacted messages.
                detail = response.json().get("detail", "unknown error")
                raise AssertionError(f"{label}: status={response.status_code}; {detail}")
            data = response.json()
            assert data["demo"] is False, f"{label}: demo mode instead of live Gemini"
            assert data["recommended"]["text"].strip()
            assert len(data["alternatives"]) == 2
            assert all(option["text"].strip() for option in data["alternatives"])
            print(f"PASS: {label} generated three validated suggestions (contents omitted).")

        history = client.get(f"/api/matches/{match_id}/messages")
        assert len(history.json()) == 1, "AI generation must not auto-record messages"
        print("PASS: conversation history remained unchanged.")
print("Live Gemini smoke test completed. No real personal data was used.")
