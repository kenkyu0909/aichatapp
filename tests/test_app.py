"""Offline behavior and privacy checks; never contact Gemini."""
import importlib.util
import json
import struct
import sys
import zlib
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("GEMINI_API_KEY", "")
    spec = importlib.util.spec_from_file_location("test_backend", Path(__file__).resolve().parents[1] / "app.py")
    module = importlib.util.module_from_spec(spec)
    # FastAPI/Pydantic resolve postponed annotations from sys.modules.
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    with TestClient(module.app) as test_client:
        yield test_client, module


def add_match(client, name):
    response = client.post("/api/matches", json={"name": name, "description": name + "の趣味は読書"})
    assert response.status_code == 201
    return response.json()["id"]


def png_bytes(color=(40, 120, 200)):
    output = BytesIO()
    Image.new("RGB", (1, 1), color).save(output, format="PNG")
    return output.getvalue()


def corrupt_png_pixels():
    image = png_bytes()
    position = 8
    chunks = []
    while position < len(image):
        length = struct.unpack(">I", image[position:position + 4])[0]
        kind = image[position + 4:position + 8]
        chunk_data = image[position + 8:position + 8 + length]
        position += 12 + length
        if kind == b"IDAT":
            chunk_data = b"not-a-valid-zlib-stream"
            length = len(chunk_data)
        checksum = zlib.crc32(kind + chunk_data) & 0xffffffff
        chunks.append(struct.pack(">I", length) + kind + chunk_data + struct.pack(">I", checksum))
        if kind == b"IEND":
            break
    return image[:8] + b"".join(chunks)


def test_profile_and_local_data(client):
    c, backend = client
    assert c.put("/api/profile", json={"content": "札幌に住んでいる", "avoid": "絵文字多用"}).status_code == 200
    assert c.get("/api/profile").json() == {"content": "札幌に住んでいる", "avoid": "絵文字多用"}
    assert backend.DB.exists()
    assert c.get("/api/status").json()["demo"] is True


def test_isolated_conversations_photo_not_in_ai_context(client):
    c, backend = client
    a, b = add_match(c, "相手A"), add_match(c, "相手B")
    assert c.post(f"/api/matches/{a}/messages", json={"role": "them", "body": "Aだけの会話"}).status_code == 201
    assert c.post(f"/api/matches/{b}/messages", json={"role": "them", "body": "Bだけの会話"}).status_code == 201
    assert c.put(f"/api/matches/{a}/photo", files={"file": ("pic.png", png_bytes(), "image/png")}).status_code == 200
    context = backend.build_context(backend.GenerateInput(mode="reply", match_id=a))
    serialized = str(context)
    assert "Aだけの会話" in serialized and "Bだけの会話" not in serialized
    assert "photo" not in serialized and "pic.png" not in serialized
    assert c.get(f"/api/matches/{a}/photo").status_code == 200


def test_messages_edit_delete_and_latest_sender(client):
    c, _ = client
    mid = add_match(c, "みな")
    posted = c.post(f"/api/matches/{mid}/messages", json={"role": "them", "body": "こんにちは"}).json()
    url = f"/api/matches/{mid}/messages/{posted['id']}"
    assert c.put(url, json={"role": "me", "body": "返信しました"}).status_code == 200
    assert c.post("/api/generate", json={"mode": "reply", "match_id": mid}).status_code == 400
    assert c.delete(url).status_code == 200
    assert c.get(f"/api/matches/{mid}/messages").json() == []


def test_three_candidates_and_like_mode(client):
    c, _ = client
    mid = add_match(c, "めい")
    c.post(f"/api/matches/{mid}/messages", json={"role": "them", "body": "旅行が好きです"})
    reply = c.post("/api/generate", json={"mode": "reply", "match_id": mid})
    assert reply.status_code == 200 and reply.json()["demo"] is True
    assert len(reply.json()["alternatives"]) == 2
    assert c.post("/api/generate", json={"mode": "like", "description": ""}).status_code == 400
    like = c.post("/api/generate", json={"mode": "like", "description": "カフェ巡りが好き"})
    assert like.status_code == 200 and len(like.json()["alternatives"]) == 2
    assert len(c.get(f"/api/matches/{mid}/messages").json()) == 1


def test_match_delete_cascades_and_input_validation(client):
    c, backend = client
    mid = add_match(c, "かな")
    c.post(f"/api/matches/{mid}/messages", json={"role": "them", "body": "よろしく"})
    assert c.put(f"/api/matches/{mid}/photo", files={"file": ("ok.png", png_bytes(), "image/png")}).status_code == 200
    photo_name = c.get("/api/matches").json()[0]["photo"]
    photo_path = backend.PHOTOS / photo_name
    assert photo_path.exists()
    assert c.put(f"/api/matches/{mid}/photo", files={"file": ("replacement.png", png_bytes((200, 80, 40)), "image/png")}).status_code == 200
    replacement_name = c.get("/api/matches").json()[0]["photo"]
    assert replacement_name != photo_name
    assert not photo_path.exists()
    photo_path = backend.PHOTOS / replacement_name
    assert c.put(f"/api/matches/{mid}/photo", files={"file": ("bad.jpg", b"not an image", "image/jpeg")}).status_code == 400
    assert c.delete(f"/api/matches/{mid}").status_code == 200
    assert c.get(f"/api/matches/{mid}/messages").status_code == 404
    assert not photo_path.exists()
    assert c.post("/api/matches", json={"name": "   "}).status_code == 422


def test_photo_requires_decodable_image_and_enforces_size_limit(client):
    c, _ = client
    mid = add_match(c, "画像確認用")
    invalid = b"\x89PNG\r\n\x1a\n" + b"not-a-real-png"
    assert c.put(f"/api/matches/{mid}/photo", files={"file": ("broken.png", invalid, "image/png")}).status_code == 400
    corrupt_pixels = corrupt_png_pixels()
    assert c.put(f"/api/matches/{mid}/photo", files={"file": ("corrupt-pixels.png", corrupt_pixels, "image/png")}).status_code == 400
    oversized_dimensions = bytearray(png_bytes())
    oversized_dimensions[16:24] = struct.pack(">II", 4001, 4000)
    oversized_dimensions[29:33] = struct.pack(">I", zlib.crc32(oversized_dimensions[12:29]) & 0xffffffff)
    assert c.put(f"/api/matches/{mid}/photo", files={"file": ("too-many-pixels.png", oversized_dimensions, "image/png")}).status_code == 400
    oversized = png_bytes() + b"\0" * (5 * 1024 * 1024)
    assert c.put(f"/api/matches/{mid}/photo", files={"file": ("large.png", oversized, "image/png")}).status_code == 400
    assert c.put(f"/api/matches/{mid}/photo", files={"file": ("valid.png", png_bytes(), "image/png")}).status_code == 200


def test_web_ui_is_served_without_api_key(client):
    c, _ = client
    page = c.get("/")
    assert page.status_code == 200
    assert "Matching Reply Assistant" in page.text
    assert c.get("/style.css").status_code == 200
    js = c.get("/app.js")
    assert js.status_code == 200
    assert 'fetch("/api"' in js.text


def test_counts_and_direction_settings_are_respected_in_context(client):
    c, backend = client
    mid = add_match(c, "さくら")
    c.post(f"/api/matches/{mid}/messages", json={"role": "them", "body": "カフェが好きです"})
    c.post(f"/api/matches/{mid}/messages", json={"role": "me", "body": "私も気になります"})
    match = c.get("/api/matches").json()[0]
    assert match["message_count"] == 2
    assert match["incoming_count"] == 1
    assert match["last_message"] == "私も気になります"
    settings = backend.GenerateInput(
        mode="followup", match_id=mid, count=5, tone="敬語",
        direction="質問を控えめに", extra="短文にして", show_policy=True
    )
    context = backend.build_context(settings)
    assert context["reply_preferences"]["tone"] == "敬語"
    assert context["reply_preferences"]["candidate_count"] == 5
    assert context["reply_preferences"]["extra"] == "短文にして"
    result = c.post("/api/generate", json=settings.model_dump())
    assert result.status_code == 200
    assert len(result.json()["alternatives"]) == 4
    assert result.json()["demo"] is True
    assert c.post("/api/generate", json={"mode": "reply", "match_id": mid}).status_code == 400


def test_single_candidate_and_invalid_count(client):
    c, _ = client
    result = c.post("/api/generate", json={"mode": "like", "count": 1, "description": "映画が趣味です"})
    assert result.status_code == 200
    assert result.json()["alternatives"] == []
    result = c.post("/api/generate", json={"mode": "like", "count": 2, "description": "映画が趣味です"})
    assert result.status_code == 422


def test_gemini_request_mock_never_sends_photo_or_other_match(client, monkeypatch):
    """This mocks the SDK client; no external API request occurs."""
    from google import genai

    c, _ = client
    c.put("/api/profile", json={"content": "架空の人物：学生", "avoid": "大げさなお世辞"})
    a, b = add_match(c, "架空の相手A"), add_match(c, "架空の相手B")
    c.post(f"/api/matches/{a}/messages", json={"role": "them", "body": "Aの架空の会話"})
    c.post(f"/api/matches/{b}/messages", json={"role": "them", "body": "Bの架空の会話"})
    c.put(f"/api/matches/{a}/photo", files={"file": ("test.png", png_bytes(), "image/png")})

    captures = []
    class FakeModels:
        def generate_content(self, **kwargs):
            captures.append(kwargs)
            return SimpleNamespace(text=json.dumps({
                "recommended": {"label": "自然体", "text": "そのお話、気になります！"},
                "alternatives": [
                    {"label": "短め", "text": "いいですね！"},
                    {"label": "質問", "text": "どんな感じなんですか？"},
                ],
                "reason": "相手の発言に自然に反応できるため。",
                "strategy": "まずは会話を広げる。"
            }, ensure_ascii=False))
    monkeypatch.setenv("GEMINI_API_KEY", "testing-only-placeholder-key")
    monkeypatch.setattr(genai, "Client", lambda **kwargs: SimpleNamespace(models=FakeModels()))
    resp = c.post("/api/generate", json={
        "mode": "reply", "match_id": a, "count": 3,
        "tone": "敬語", "direction": "質問を控えめに"
    })
    assert resp.status_code == 200, resp.text
    assert resp.json()["demo"] is False
    assert len(captures) == 1
    payload = captures[0]["contents"]
    assert "Aの架空の会話" in payload
    assert "Bの架空の会話" not in payload
    assert "photo" not in payload and "test.png" not in payload
    assert "testing-only-placeholder-key" not in payload
    assert "質問を控えめに" in payload
    assert len(c.get(f"/api/matches/{a}/messages").json()) == 1


def test_long_history_is_limited_and_missing_match_is_rejected(client):
    c, backend = client
    mid = add_match(c, "履歴上限確認")
    for index in range(65):
        c.post(f"/api/matches/{mid}/messages", json={"role": "them", "body": f"架空の発言{index}"})
    settings = backend.GenerateInput(mode="reply", match_id=mid)
    history = backend.build_context(settings)["history"]
    assert len(history) == 60
    assert history[0]["body"] == "架空の発言5"
    assert c.post("/api/generate", json={"mode": "reply", "match_id": 9999}).status_code == 404


@pytest.mark.parametrize("response_text", [
    "not-json",
    json.dumps({
        "recommended": {"label": "おすすめ", "text": "同じ文章です"},
        "alternatives": [
            {"label": "別案1", "text": "同じ文章です"},
            {"label": "別案2", "text": "別の文章です"},
        ],
        "reason": "架空テスト",
        "strategy": "架空テスト",
    }, ensure_ascii=False),
    json.dumps({
        "recommended": {"label": "おすすめ", "text": "一つだけの文章です"},
        "alternatives": [],
        "reason": "架空テスト",
        "strategy": "架空テスト",
    }, ensure_ascii=False),
])
def test_malformed_or_duplicate_gemini_response_is_not_shown_as_generated(client, monkeypatch, response_text):
    from google import genai

    c, _ = client
    mid = add_match(c, "出力検証")
    c.post(f"/api/matches/{mid}/messages", json={"role": "them", "body": "架空の会話"})

    class FakeModels:
        def generate_content(self, **kwargs):
            return SimpleNamespace(text=response_text)

    monkeypatch.setenv("GEMINI_API_KEY", "testing-only-placeholder-key")
    monkeypatch.setattr(genai, "Client", lambda **kwargs: SimpleNamespace(models=FakeModels()))
    response = c.post("/api/generate", json={"mode": "reply", "match_id": mid, "count": 3})
    assert response.status_code == 502
    assert response.json()["detail"] == "AIの応答形式が不正でした。再生成してください。"
    assert len(c.get(f"/api/matches/{mid}/messages").json()) == 1


def test_quota_error_is_redacted_and_does_not_change_history(client, monkeypatch):
    from google import genai

    c, _ = client
    mid = add_match(c, "制限検証")
    c.post(f"/api/matches/{mid}/messages", json={"role": "them", "body": "架空の会話"})

    class FakeModels:
        def generate_content(self, **kwargs):
            raise RuntimeError("429 synthetic private SDK detail")

    monkeypatch.setenv("GEMINI_API_KEY", "testing-only-placeholder-key")
    monkeypatch.setattr(genai, "Client", lambda **kwargs: SimpleNamespace(models=FakeModels()))
    response = c.post("/api/generate", json={"mode": "reply", "match_id": mid})
    assert response.status_code == 502
    assert "制限に達しました" in response.json()["detail"]
    assert "synthetic private SDK detail" not in response.text
    assert len(c.get(f"/api/matches/{mid}/messages").json()) == 1
