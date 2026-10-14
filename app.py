"""Private, localhost-only matching-app writing assistant."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
DATA = Path(os.getenv("APP_DATA_DIR", str(BASE / "data"))).resolve()
PHOTOS = DATA / "photos"
DB = DATA / "app.sqlite3"
PROMPTS = BASE / "prompts"
DATA.mkdir(parents=True, exist_ok=True)
PHOTOS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Matching Reply Assistant", docs_url=None, redoc_url=None)


@contextmanager
def database():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


with database() as db:
    db.executescript("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            content TEXT NOT NULL DEFAULT '',
            avoid TEXT NOT NULL DEFAULT ''
        );
        INSERT OR IGNORE INTO profile (id, content, avoid) VALUES (1, '', '');
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            photo TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            role TEXT NOT NULL CHECK (role IN ('me', 'them')),
            body TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)


class ProfileInput(BaseModel):
    content: str = Field(max_length=12000)
    avoid: str = Field(default="", max_length=4000)


class MatchInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=12000)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("名前を入力してください")
        return value.strip()


class MessageInput(BaseModel):
    role: Literal["me", "them"]
    body: str = Field(min_length=1, max_length=12000)

    @field_validator("body")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("空のメッセージは保存できません")
        return value.strip()


class GenerateInput(BaseModel):
    mode: Literal["reply", "like", "followup"]
    match_id: int | None = None
    name: str = Field(default="", max_length=100)
    description: str = Field(default="", max_length=12000)
    count: Literal[1, 3, 5] = 3
    tone: Literal["自動", "敬語", "混合", "タメ口"] = "自動"
    direction: str = Field(default="", max_length=120)
    extra: str = Field(default="", max_length=1000)
    show_policy: bool = False


class Candidate(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    text: str = Field(min_length=1, max_length=1000)


class Suggestions(BaseModel):
    recommended: Candidate
    alternatives: list[Candidate] = Field(default_factory=list, max_length=4)
    reason: str = Field(min_length=1, max_length=500)
    strategy: str = Field(default="", max_length=500)


def one_match(db: sqlite3.Connection, match_id: int) -> dict:
    row = db.execute("SELECT * FROM matches WHERE id=?", (match_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "相手が見つかりません")
    return dict(row)


def one_message(db: sqlite3.Connection, match_id: int, message_id: int) -> dict:
    one_match(db, match_id)
    row = db.execute(
        "SELECT * FROM messages WHERE id=? AND match_id=?", (message_id, match_id)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "メッセージが見つかりません")
    return dict(row)


@app.get("/")
def index():
    return FileResponse(BASE / "index.html", media_type="text/html", headers={"Cache-Control": "no-store"})


@app.get("/style.css")
def stylesheet():
    return FileResponse(BASE / "style.css", media_type="text/css", headers={"Cache-Control": "no-store"})


@app.get("/app.js")
def frontend_script():
    return FileResponse(BASE / "app.js", media_type="application/javascript", headers={"Cache-Control": "no-store"})


@app.get("/api/status")
def status():
    return {
        "demo": not bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    }


@app.get("/api/profile")
def get_profile():
    with database() as db:
        return dict(db.execute("SELECT content, avoid FROM profile WHERE id=1").fetchone())


@app.put("/api/profile")
def put_profile(data: ProfileInput):
    with database() as db:
        db.execute(
            "UPDATE profile SET content=?, avoid=? WHERE id=1",
            (data.content, data.avoid),
        )
    return {"ok": True}


@app.get("/api/matches")
def get_matches():
    with database() as db:
        return [
            dict(r) for r in db.execute(
                "SELECT * FROM matches ORDER BY id DESC"
            ).fetchall()
        ]


@app.post("/api/matches", status_code=201)
def add_match(data: MatchInput):
    with database() as db:
        cur = db.execute(
            "INSERT INTO matches(name, description) VALUES (?,?)",
            (data.name, data.description),
        )
        return one_match(db, cur.lastrowid)


@app.put("/api/matches/{match_id}")
def put_match(match_id: int, data: MatchInput):
    with database() as db:
        one_match(db, match_id)
        db.execute(
            "UPDATE matches SET name=?, description=? WHERE id=?",
            (data.name, data.description, match_id),
        )
        return one_match(db, match_id)


@app.delete("/api/matches/{match_id}")
def delete_match(match_id: int):
    with database() as db:
        match = one_match(db, match_id)
        db.execute("DELETE FROM matches WHERE id=?", (match_id,))
    if match["photo"]:
        (PHOTOS / match["photo"]).unlink(missing_ok=True)
    return {"ok": True}


def image_extension(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


@app.put("/api/matches/{match_id}/photo")
async def upload_photo(match_id: int, file: UploadFile = File(...)):
    with database() as db:
        match = one_match(db, match_id)
    raw = await file.read(5 * 1024 * 1024 + 1)
    await file.close()
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(400, "写真は5MB以下にしてください")
    ext = image_extension(raw)
    if not ext:
        raise HTTPException(400, "JPEG・PNG・WebP画像のみ登録できます")
    filename = uuid.uuid4().hex + ext
    (PHOTOS / filename).write_bytes(raw)
    try:
        with database() as db:
            one_match(db, match_id)
            db.execute("UPDATE matches SET photo=? WHERE id=?", (filename, match_id))
    except Exception:
        (PHOTOS / filename).unlink(missing_ok=True)
        raise
    if match["photo"]:
        (PHOTOS / match["photo"]).unlink(missing_ok=True)
    return {"ok": True}


@app.get("/api/matches/{match_id}/photo")
def read_photo(match_id: int):
    with database() as db:
        match = one_match(db, match_id)
    if not match["photo"]:
        raise HTTPException(404, "写真は未登録です")
    filepath = PHOTOS / match["photo"]
    if not filepath.is_file():
        raise HTTPException(404, "写真が見つかりません")
    return FileResponse(filepath, headers={"Cache-Control": "private, no-store"})


@app.get("/api/matches/{match_id}/messages")
def list_messages(match_id: int):
    with database() as db:
        one_match(db, match_id)
        return [
            dict(r) for r in db.execute(
                "SELECT * FROM messages WHERE match_id=? ORDER BY id",
                (match_id,),
            )
        ]


@app.post("/api/matches/{match_id}/messages", status_code=201)
def add_message(match_id: int, data: MessageInput):
    with database() as db:
        one_match(db, match_id)
        cur = db.execute(
            "INSERT INTO messages(match_id, role, body) VALUES (?,?,?)",
            (match_id, data.role, data.body),
        )
        return one_message(db, match_id, cur.lastrowid)


@app.put("/api/matches/{match_id}/messages/{message_id}")
def put_message(match_id: int, message_id: int, data: MessageInput):
    with database() as db:
        one_message(db, match_id, message_id)
        db.execute(
            "UPDATE messages SET role=?,body=? WHERE id=? AND match_id=?",
            (data.role, data.body, message_id, match_id),
        )
        return one_message(db, match_id, message_id)


@app.delete("/api/matches/{match_id}/messages/{message_id}")
def delete_message(match_id: int, message_id: int):
    with database() as db:
        one_message(db, match_id, message_id)
        db.execute(
            "DELETE FROM messages WHERE id=? AND match_id=?", (message_id, match_id)
        )
    return {"ok": True}


def build_context(data: GenerateInput) -> dict:
    """Never include photos, local paths, API keys or other matches."""
    with database() as db:
        profile = dict(
            db.execute("SELECT content,avoid FROM profile WHERE id=1").fetchone()
        )
        if data.mode == "like":
            if not data.description.strip():
                raise HTTPException(400, "相手のプロフィール文を入力してください")
            other = {"name": data.name.strip(), "description": data.description.strip()}
            history = []
        else:
            if data.match_id is None:
                raise HTTPException(400, "相手を選択してください")
            match = one_match(db, data.match_id)
            other = {"name": match["name"], "description": match["description"]}
            records = db.execute(
                "SELECT role,body FROM messages WHERE match_id=? ORDER BY id DESC LIMIT 60",
                (data.match_id,),
            ).fetchall()
            history = [dict(row) for row in reversed(records)]
            if not history:
                raise HTTPException(400, "先に会話履歴を追加してください")
            if data.mode == "reply" and history[-1]["role"] == "me":
                raise HTTPException(
                    400, "最後のメッセージが自分の発言です。相手からの返信が来てから生成してください"
                )
    return {
        "mode": data.mode,
        "my_profile": profile,
        "other": other,
        "history": history,
        "reply_preferences": {
            "tone": data.tone,
            "direction": data.direction,
            "extra": data.extra,
            "candidate_count": data.count,
            "show_policy": data.show_policy,
        },
    }


def check_suggestions(value: Suggestions, count: int) -> dict:
    candidates = [value.recommended, *value.alternatives]
    normalized = [re.sub(r"\\s+", "", c.text) for c in candidates]
    if len(candidates) != count or len(set(normalized)) != count:
        raise ValueError("候補の数または重複が不正です")
    return value.model_dump()


def demo_suggestions(mode: str, count: int) -> dict:
    """APIキーなしの場合のみ。AI生成と誤解しない固定例文です。"""
    if mode == "like":
        texts = [
            ("自然体", "はじめまして！プロフィールを読んで気になりました。よかったらお話ししてみたいです！"),
            ("親しみやすく", "はじめまして！紹介文が気になっていいねしました。よろしくお願いします！"),
            ("短め", "はじめまして！よければ少しお話しできたらうれしいです。"),
            ("丁寧", "プロフィールを拝見して、お話ししてみたいと思いました。よろしくお願いします！"),
            ("カジュアル", "はじめまして！お話できたらうれしいです！"),
        ]
    elif mode == "followup":
        texts = [
            ("自然体", "そういえば、前にお話していたことが少し気になっていました！"),
            ("控えめ", "またお時間があるときにお話しできたらうれしいです。"),
            ("カジュアル", "こんにちは！最近どう過ごしてますか？"),
            ("一言", "またお話しできたらうれしいです！"),
            ("別の話題", "そういえば、最近気になっていることってありますか？"),
        ]
    else:
        texts = [
            ("自然体", "そうなんですね！もう少し詳しく聞いてみたいです。"),
            ("親しみやすく", "なるほど、そんな感じなんですね！ちょっと気になります。"),
            ("会話を広げる", "教えてくれてありがとうございます！どんなところが好きなんですか？"),
            ("短め", "それは楽しそうですね！"),
            ("気持ちに寄り添う", "話してくれてありがとうございます！"),
        ]
    selected = texts[:count]
    return {
        "recommended": {"label": selected[0][0], "text": selected[0][1]},
        "alternatives": [{"label": a, "text": b} for a, b in selected[1:]],
        "reason": "APIキー未設定のため、会話内容を解析しない固定例文を表示しています。",
        "strategy": "デモ表示です。実際の状況を分析した提案ではありません。",
        "demo": True,
    }


def read_prompt(mode: str) -> str:
    return (PROMPTS / ("like.txt" if mode == "like" else "reply.txt")).read_text(
        encoding="utf-8"
    )


@app.post("/api/generate")
def generate(data: GenerateInput):
    context = build_context(data)
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return demo_suggestions(data.mode, data.count)

    system_instruction = read_prompt(data.mode) + (
        f"\\n【今回の出力指定】候補は必ず合計{data.count}案にしてください。"
        f"recommendedが1案、alternativesが{data.count-1}案です。"
        "理由 reason は短く日本語で、会話方針 strategy は無理のない提案を1文で記述してください。"
        + ("追いメッセージを検討してください。相手に圧力をかけないでください。" if data.mode == "followup" else "")
    )
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            contents=json.dumps(context, ensure_ascii=False),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.8,
                response_mime_type="application/json",
                response_schema=Suggestions,
            ),
        )
        if not response.text:
            raise ValueError("AIから応答がありません")
        parsed = Suggestions.model_validate_json(response.text)
        return {**check_suggestions(parsed, data.count), "demo": False}
    except Exception as exc:
        error_text = str(exc).lower()
        if "429" in error_text or "resource_exhausted" in error_text:
            message = "Geminiの無料利用枠またはレート制限に達しました。AI Studioで上限を確認してください。"
        elif "401" in error_text or "403" in error_text or "api_key" in error_text:
            message = "Gemini APIキーまたはモデルの利用権限を確認してください。"
        elif "404" in error_text or "not found" in error_text:
            message = "モデルが見つかりません。.envのGEMINI_MODELを確認してください。"
        elif isinstance(exc, (ValueError, json.JSONDecodeError)):
            message = "AIの応答形式が不正でした。再生成してください。"
        else:
            message = "Geminiとの通信に失敗しました。接続と設定を確認してください。"
        # Do not expose raw SDK errors: they may include user data or credentials.
        raise HTTPException(status_code=502, detail=message) from None
