import json
import os
from typing import Optional
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

from .database import get_db, init_db

app = FastAPI(title="Matching Reply AI Assistant")
init_db()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

app.mount("/static", StaticFiles(directory="static"), name="static")

def load_my_profile_from_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, updated_at FROM my_profile WHERE id = 1")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO my_profile (id) VALUES (1)")
        conn.commit()
        row = cursor.fetchone()
    cursor.execute("SELECT field_name, field_value FROM profile_fields WHERE profile_id = 1")
    fields = {row["field_name"]: row["field_value"] for row in cursor.fetchall()}
    conn.close()
    return {"id": row["id"], "fields": fields}

def save_profile_to_db(fields):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profile_fields WHERE profile_id = 1")
    for field_name, field_value in fields.items():
        if field_value:
            cursor.execute("INSERT INTO profile_fields (profile_id, field_name, field_value) VALUES (1, ?, ?)", (field_name, field_value))
    cursor.execute("UPDATE my_profile SET updated_at = CURRENT_TIMESTAMP WHERE id = 1")
    conn.commit()
    conn.close()

def get_all_matches_from_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, profile, image_path FROM matches ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row["id"], "name": row["name"], "profile": row["profile"], "image_path": row["image_path"]} for row in rows]

def create_match_in_db(name, profile="", image_path=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO matches (name, profile, image_path) VALUES (?, ?, ?)", (name, profile, image_path))
    match_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return match_id

def get_match_from_db(match_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, profile, image_path FROM matches WHERE id = ?", (match_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "name": row["name"], "profile": row["profile"], "image_path": row["image_path"]}
    return None

def delete_match_in_db(match_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE match_id = ?", (match_id,))
    cursor.execute("DELETE FROM matches WHERE id = ?", (match_id,))
    conn.commit()
    conn.close()

def get_messages_from_db(match_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, match_id, sender, text, created_at FROM messages WHERE match_id = ? ORDER BY created_at", (match_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row["id"], "match_id": row["match_id"], "sender": row["sender"], "text": row["text"], "created_at": row["created_at"]} for row in rows]

def add_message_to_db(match_id, sender, text):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (match_id, sender, text) VALUES (?, ?, ?)", (match_id, sender, text))
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id

class GenerateReplyRequest(BaseModel):
    mode: str = "reply"
    match_id: Optional[int] = None
    conversation_history: list = Field(default_factory=list)
    my_profile_fields: dict = Field(default_factory=dict)

class GenerateLikeRequest(BaseModel):
    mode: str = "like"
    match_id: Optional[int] = None
    partner_profile: str = ""
    partner_name: Optional[str] = None
    my_profile_fields: dict = Field(default_factory=dict)

app = FastAPI(title="Matching Reply AI Assistant")
init_db()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.get("/api/matches")
async def get_matches_api():
    return {"matches": get_all_matches_from_db()}

@app.post("/api/matches")
async def create_match_api(name, profile="", image_path=""):
    match_id = create_match_in_db(name, profile, image_path)
    return {"match_id": match_id, "status": "ok"}

@app.delete("/api/matches/{match_id}")
async def remove_match(match_id):
    delete_match_in_db(match_id)
    return {"status": "ok"}

@app.get("/api/messages/{match_id}")
async def get_messages_api(match_id):
    messages = get_messages_from_db(match_id)
    return {"messages": messages}

@app.post("/api/messages")
async def add_message_api(match_id, sender, text):
    msg_id = add_message_to_db(match_id, sender, text)
    return {"message_id": msg_id, "status": "ok"}

@app.post("/api/generate/reply")
async def generate_reply(request: GenerateReplyRequest):
    if not os.getenv("GEMINI_API_KEY"):
        return {"status": "success", "data": generate_mock_reply(request)}
    my_profile = load_my_profile_from_db()
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = "test prompt"
        response = model.generate_content(prompt)
        result = {"recommended": {"label": "自然体", "text": "test"}, "alternatives": [], "reason": "test"}
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO generation_log (match_id, mode, input_summary, output_json) VALUES (?, ?, ?, ?)", 
            (request.match_id, request.mode, "test", json.dumps(result)))
        conn.commit()
        conn.close()
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"Gemini error: {e}")
        return {"status": "success", "data": generate_mock_reply(request)}

def generate_mock_reply(request):
    return {"status": "success", "data": {"recommended": {"label": "自然体", "text": "テスト"}, "alternatives": [], "reason": "テスト"}}

@app.post("/api/generate/like")
async def generate_like(request: GenerateLikeRequest):
    if not os.getenv("GEMINI_API_KEY"):
        return {"status": "success", "data": generate_mock_like(request)}
    return {"status": "success", "data": generate_mock_like(request)}

def generate_mock_like(request):
    return {"status": "success", "data": {"recommended": {"label": "自然体", "text": "テスト"}, "alternatives": [], "reason": "テスト"}}

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
