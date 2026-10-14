"""Run a fictional, resumable conversation through the existing FastAPI app."""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "docs" / "verification" / "simulations"
PROFILE_FILE = SIM_DIR / "profiles.md"
JSON_FILE = SIM_DIR / "conversation_001.json"
HTML_FILE = SIM_DIR / "conversation_001.html"
DATA_DIR = Path(tempfile.gettempdir()) / "mra-conversation-001-sandbox"
MAX_APP_MESSAGES = 20
MODEL_ORDER = (
    ("API1", "gemini-3.5-flash-lite"),
    ("API2", "gemini-3.5-flash-lite"),
    ("API1", "gemini-3.1-flash-lite"),
    ("API2", "gemini-3.1-flash-lite"),
)

SELF = {
    "name": "佐倉みなと", "age": 26, "region": "神奈川県横浜市", "occupation": "Webデザイナー",
    "hobbies": ["喫茶店めぐり", "読書", "近場の散歩"],
    "profile": "横浜でWebデザイナーをしています。休日は喫茶店で本を読んだり、近場を散歩したりしています。カレーとプリンが好きです。まずは自然にお話しできたらうれしいです。",
    "avoid": "大げさな褒め言葉、根拠のない共通点、返信を急かす言葉。短く自然な日本語を好み、質問攻めは避けたいです。",
}
PARTNER_PUBLIC = {
    "name": "小川あかり", "age": 25, "region": "東京都世田谷区", "occupation": "美術館の広報",
    "hobbies": ["美術館", "喫茶店", "短い旅行"],
    "profile": "世田谷区に住んでいて、美術館の広報をしています。休日は展覧会を見たり、友人と喫茶店に行ったりします。スパイスカレーと季節のケーキが好きです。穏やかに話せる方だとうれしいです。",
    "conversation_style": "話題を共有しながら自然に続く会話。質問は一度に一つ程度。互いの都合を尊重する。",
}
PARTNER_INTERNAL = (
    "会話の反応に応じて少しずつ親しくなる。短文や質問を返さない返事も使う。急な誘いや押しの強さには慎重。"
    "会話から安心感と関心が生まれた場合は誘いに応じる可能性があるが、成功条件を理由に結果を操作しない。"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_state() -> dict[str, Any]:
    return {
        "schema_version": 1, "experiment_id": "conversation_001", "started_at": utc_now(),
        "updated_at": utc_now(), "status": "RUNNING", "end_reason": None,
        "people": {"app_user": SELF, "partner_public": PARTNER_PUBLIC, "partner_internal": PARTNER_INTERNAL},
        "environment": {"os": "Windows", "browser_for_report": "Firefox", "database": "架空データ専用の一時SQLite"},
        "api_requests": [], "messages": [], "turns": [], "app_sent_count": 0,
        "partner_sent_count": 0, "first_invite_app_message": None, "meeting_agreement": None,
        "assessment": {},
    }


def save_state(state: dict[str, Any], path: Path = JSON_FILE) -> None:
    state["updated_at"] = utc_now()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def export_profiles(path: Path = PROFILE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 会話シミュレーション用の架空プロフィール\n\n実験ID: `conversation_001`（2026-10-14）\n\n"
        "## アプリ側（本人役）\n\n"
        f"- 名前・年齢: {SELF['name']}、{SELF['age']}歳\n- 居住地・仕事: {SELF['region']}、{SELF['occupation']}\n"
        f"- 趣味: {', '.join(SELF['hobbies'])}\n- 公開プロフィール: {SELF['profile']}\n- 避けたい表現: {SELF['avoid']}\n\n"
        "## 相手役の公開プロフィール（アプリ/Geminiに渡す情報）\n\n"
        f"- 名前・年齢: {PARTNER_PUBLIC['name']}、{PARTNER_PUBLIC['age']}歳\n"
        f"- 居住地・仕事: {PARTNER_PUBLIC['region']}、{PARTNER_PUBLIC['occupation']}\n"
        f"- 趣味: {', '.join(PARTNER_PUBLIC['hobbies'])}\n- 公開プロフィール: {PARTNER_PUBLIC['profile']}\n"
        f"- 会話スタイル: {PARTNER_PUBLIC['conversation_style']}\n\n"
        "## 相手役の内部設定（Codexのみ。アプリ/Geminiには送信しない）\n\n"
        f"{PARTNER_INTERNAL}\n", encoding="utf-8",
    )


def can_send_app(state: dict[str, Any]) -> bool:
    return state["status"] == "RUNNING" and state["app_sent_count"] < MAX_APP_MESSAGES


def send_app_message(state: dict[str, Any], body: str, turn: dict[str, Any]) -> int:
    if not can_send_app(state):
        raise RuntimeError("実験終了またはアプリ側の送信上限20通に達しています")
    state["app_sent_count"] += 1
    number = state["app_sent_count"]
    message = {"sequence": len(state["messages"]) + 1, "speaker": "app", "body": body,
               "app_send_number": number, "at": utc_now()}
    if not state["first_invite_app_message"] and re.search(r"(ご飯|食事|カフェ|喫茶店|ランチ|散歩).{0,25}(行|会)|今度.{0,20}(会|行)", body):
        state["first_invite_app_message"] = number
        message["is_invite"] = True
    state["messages"].append(message)
    turn["selected_text"] = body
    turn["app_send_number"] = number
    state["turns"].append(turn)
    return number


def send_partner_message(state: dict[str, Any], body: str) -> int:
    if state["status"] != "RUNNING":
        raise RuntimeError("実験終了後は相手メッセージを追加できません")
    state["partner_sent_count"] += 1
    state["messages"].append({"sequence": len(state["messages"]) + 1, "speaker": "partner", "body": body, "at": utc_now()})
    return len(state["messages"])


def fallback_slot(rate_limited: bool, current_index: int) -> int | None:
    return current_index + 1 if rate_limited and 0 <= current_index < len(MODEL_ORDER) - 1 else None


def has_concrete_meeting_agreement(app_proposal: str, partner_reply: str) -> bool:
    positive = re.search(r"(いいですね|大丈夫|ぜひ|行きましょう|お願いします|楽しみです|問題ない)", partner_reply)
    negative = re.search(r"(難しい|無理|行けません|ごめんなさい|やめて|会いたくない|また今度|まだ分からない|まだわからない|後で|あとで|未定|もし|都合が合えば|予定が分からない|予定がわからない)", partner_reply)
    date = re.search(r"(月|火|水|木|金|土|日)曜|\d{1,2}月\d{1,2}日", app_proposal)
    time = re.search(r"(午前|午後)?\s*\d{1,2}時|\d{1,2}:\d{2}", app_proposal)
    place = re.search(r"(駅|カフェ|喫茶店|レストラン|店|公園|美術館|場所|丁目)", app_proposal)
    return bool(positive and not negative and date and time and place)


def confirm_meeting_success(state: dict[str, Any]) -> None:
    """Finalize SUCCESS only after an explicit operator review of saved utterances."""
    pending = state.get("pending_meeting_confirmation")
    if not pending or not has_concrete_meeting_agreement(pending["proposal"], pending["acceptance"]):
        raise ValueError("日時・場所を含む提案と明確な相手の承諾を確認できません")
    state["status"] = "SUCCESS"
    state["meeting_agreement"] = {"proposal": pending["proposal"], "acceptance": pending["acceptance"]}
    state["end_reason"] = "評価者が保存済みの発言を確認し、具体的な日時・場所と相手の明確な承諾を確認しました。"
    for message in state["messages"][-2:]:
        message["meeting_agreement"] = True


def render_html(state: dict[str, Any], path: Path = HTML_FILE) -> None:
    e = lambda value: html.escape(str(value if value is not None else ""), quote=True)
    labels = {"SUCCESS": "会う約束が成立", "LIMIT_REACHED": "送信上限到達", "SAFETY_STOP": "安全上の停止", "BLOCKED": "技術的に中断", "RUNNING": "実験中"}
    me, partner = state["people"]["app_user"], state["people"]["partner_public"]
    model = next((r.get("model") for r in reversed(state["api_requests"]) if r.get("ok")), "未接続")
    by_send = {t.get("app_send_number"): t for t in state["turns"] if t.get("app_send_number")}
    bubbles = []
    for m in state["messages"]:
        app_side = m["speaker"] == "app"
        turn = by_send.get(m.get("app_send_number"), {})
        details = ""
        if app_side and turn:
            items = "".join(f"<li><b>{e(c.get('label'))}</b>：{e(c.get('text'))}</li>" for c in turn.get("candidates", []))
            details = ("<details><summary>この返信の生成結果を見る</summary>"
                       f"<p><b>理由：</b>{e(turn.get('reason'))}</p><p><b>会話方針：</b>{e(turn.get('strategy'))}</p>"
                       f"<p><b>選択理由：</b>{e(turn.get('selection_reason'))}</p><p><b>モデル：</b>{e(turn.get('model'))} / API: {e(turn.get('api_status'))}</p>"
                       f"<p><b>文体：</b>{e(turn.get('settings',{}).get('tone'))} / <b>方向：</b>{e(turn.get('settings',{}).get('direction'))} / <b>追加指示：</b>{e(turn.get('settings',{}).get('extra') or 'なし')}</p>"
                       f"<ol>{items}</ol></details>")
        badges = "初めての誘い" if m.get("is_invite") else ""
        badges += " / 約束の合意" if m.get("meeting_agreement") else ""
        label = "アプリ側（Gemini候補から選択）" if app_side else "相手役（Codex）"
        count = f"送信 {m['app_send_number']}通目" if app_side else ""
        bubbles.append(f"<article class='row {'right' if app_side else 'left'}'><div class='bubble {'app' if app_side else 'partner'}'>"
                       f"<small>{e(label)}　{e(count)}　<b class='badge'>{e(badges)}</b></small><p>{e(m['body'])}</p>{details}</div></article>")
    cards = []
    for title, person, private in (("本人役", me, False), ("相手役の公開プロフィール", partner, False),
                                   ("相手役の内部設定（Codexのみ）", {"profile": state["people"].get("partner_internal", "")}, True)):
        info = "".join(f"<li><b>{e(k)}</b>：{e(', '.join(v) if isinstance(v,list) else v)}</li>"
                       for k,v in person.items() if k not in ("profile", "internal", "avoid"))
        text = person.get("profile", "")
        cards.append(f"<section class='profile {'private' if private else ''}'><h3>{e(title)}</h3><ul>{info}</ul><p>{e(text)}</p>"
                     f"{'<small>アプリ/Geminiへは送信していません。</small>' if private else ''}</section>")
    scores = state.get("assessment", {}).get("scores", {})
    score_html = "".join(f"<li><b>{e(k)}</b>：{e(v.get('score','未評価'))}{'/5' if str(v.get('score','')).isdigit() else ''} — {e(v.get('reason','根拠未記録'))}</li>" for k,v in scores.items())
    assessment = state.get("assessment", {})
    doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Matching Reply Assistant — AI会話シミュレーション</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:#243247;font:16px/1.65 system-ui,"Yu Gothic",Meiryo,sans-serif}}header,main,footer{{max-width:1050px;margin:auto;padding:22px}}h1{{font-size:clamp(1.4rem,4vw,2rem)}}h2{{margin-top:28px}}.overview,.profile,.chat,.result{{background:white;border:1px solid #dce4ee;border-radius:16px;padding:18px;box-shadow:0 3px 14px #2034500b}}.facts,.profiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}.private{{border:1px dashed #bd9c65;background:#fffaf0}}.chat{{padding:14px;max-height:78vh;overflow:auto}}.row{{display:flex;margin:14px 0}}.right{{justify-content:flex-end}}.left{{justify-content:flex-start}}.bubble{{max-width:min(82%,700px);padding:12px 15px;border-radius:17px;overflow-wrap:anywhere}}.bubble p{{white-space:pre-wrap;margin:8px 0 0}}.app{{background:#dff3e7;border-bottom-right-radius:4px}}.partner{{background:#e8edf5;border-bottom-left-radius:4px}}small{{font-size:.8rem;color:#506078}}.badge{{color:#9b4b17}}details{{border-top:1px solid #b8cbbf;margin-top:10px;padding-top:8px}}summary{{cursor:pointer;font-weight:650}}footer{{color:#596779;font-size:.88rem}}@media(max-width:600px){{header,main,footer{{padding:14px}}.bubble{{max-width:94%}}}}
</style></head><body><header><h1>Matching Reply Assistant — AI会話シミュレーション</h1><section class="overview"><div class="facts"><div>実験日時<br>{e(state.get('started_at'))}</div><div>実験ID<br>{e(state.get('experiment_id'))}</div><div>使用モデル<br>{e(model)}</div><div>終了状態<br>{e(labels.get(state['status'],state['status']))} ({e(state['status'])})</div><div>アプリ側<br>{e(me['name'])}</div><div>相手役<br>{e(partner['name'])}</div><div>送信数<br>アプリ {state['app_sent_count']} / 相手 {state['partner_sent_count']}</div><div>会話メッセージ数<br>{len(state['messages'])}</div><div>Geminiリクエスト<br>{len(state['api_requests'])}回</div></div><p><b>終了理由：</b>{e(state.get('end_reason') or '未記録')}</p></section></header><main><h2>プロフィール</h2><div class="profiles">{''.join(cards)}</div><h2>会話記録</h2><section class="chat">{''.join(bubbles) or '<p>会話メッセージはありません。</p>'}</section><section class="result"><h2>実験結果と品質評価</h2><p>{e(assessment.get('summary','評価未記録'))}</p><p><b>初めて誘った送信番号：</b>{e(state.get('first_invite_app_message') or 'なし')}</p><p><b>日時・場所の合意：</b>{e(json.dumps(state.get('meeting_agreement'),ensure_ascii=False) if state.get('meeting_agreement') else 'なし')}</p><ol>{score_html or '<li>評価は未実施です。</li>'}</ol><p><b>評価上の制限：</b>Codexが相手役と評価役を兼ねるため、評価にバイアスが含まれる可能性があります。</p><p><b>改善点：</b>{e(assessment.get('improvements','未記録'))}</p></section></main><footer>単体HTML。外部通信・CDN・外部スクリプト・外部画像はありません。架空データのみ。</footer></body></html>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")


def extract_key(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    matches = re.findall(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{30,}(?![A-Za-z0-9_-])", text)
    if len(matches) != 1:
        raise ValueError(f"{path.stem}: APIキー候補を一意に判別できません")
    return matches[0]


def import_app(data_dir: Path):
    os.environ["APP_DATA_DIR"] = str(data_dir)
    sys.path.insert(0, str(ROOT))
    from fastapi.testclient import TestClient
    import app as backend
    return TestClient(backend.app)


def api_sources(api_dir: Path) -> dict[str, str]:
    return {"API1": extract_key(api_dir / "chat1.md"), "API2": extract_key(api_dir / "chat2.md")}


def db_matches_state(client: Any, state: dict[str, Any]) -> bool:
    response = client.get(f"/api/matches/{state['match_id']}/messages")
    if response.status_code != 200:
        return False
    expected = [("me" if m["speaker"] == "app" else "them", m["body"]) for m in state["messages"]]
    return [(m["role"], m["body"]) for m in response.json()] == expected


def main_run(api_dir: Path, opening: str | None, resume: bool,
             candidate_number: int | None, partner_reply: str | None,
             direction: str, extra: str, confirm_success: bool) -> int:
    if JSON_FILE.exists() and not resume:
        raise SystemExit("会話JSONが既にあります。既存結果を上書きしないため --resume を使ってください")
    if resume and not JSON_FILE.is_file():
        raise SystemExit("再開用のJSONログがありません")
    try:
        keys = api_sources(api_dir)
    except (OSError, ValueError) as exc:
        state = json.loads(JSON_FILE.read_text(encoding="utf-8")) if resume else new_state()
        state["status"] = "BLOCKED"
        state["end_reason"] = "指定APIフォルダーの認証情報を安全に特定できませんでした。"
        save_state(state); render_html(state); export_profiles()
        print(f"BLOCKED: APIファイルの形式を安全に確認できません ({type(exc).__name__})")
        return 2
    export_profiles()
    if not resume and DATA_DIR.exists():
        raise SystemExit("専用SQLite保存先が存在します。内容を削除せず停止しました")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    client = import_app(DATA_DIR)
    state = json.loads(JSON_FILE.read_text(encoding="utf-8")) if resume else new_state()
    if resume:
        if state.get("status") not in ("RUNNING", "BLOCKED") or state.get("experiment_id") != "conversation_001":
            raise SystemExit("実験状態がRUNNING/BLOCKEDではないため再開しません")
        if not db_matches_state(client, state):
            raise SystemExit("一時SQLiteとJSON履歴が一致しないため、状態を変更せず停止しました")
        state["status"] = "RUNNING"; state["end_reason"] = None
    else:
        client.put("/api/profile", json={"content": SELF["profile"], "avoid": SELF["avoid"]})
        created = client.post("/api/matches", json={"name": PARTNER_PUBLIC["name"], "description": PARTNER_PUBLIC["profile"]})
        if created.status_code != 201:
            raise RuntimeError("架空プロフィールの登録に失敗しました")
        state["match_id"] = created.json()["id"]
        state["environment"]["model_priority"] = [f"{a}/{m}" for a,m in MODEL_ORDER]
    match_id = state["match_id"]

    if not state["messages"]:
        if not opening:
            print("架空の相手役の開始メッセージを --opening-message で渡してください")
            state["end_reason"] = "開始メッセージ入力待ちです。"
            save_state(state); render_html(state); return 0
        result = client.post(f"/api/matches/{match_id}/messages", json={"role": "them", "body": opening})
        if result.status_code != 201:
            raise RuntimeError("開始メッセージをSQLiteへ保存できませんでした")
        send_partner_message(state, opening); save_state(state)

    if state["messages"] and state["messages"][-1]["speaker"] == "app" and partner_reply:
        if partner_reply == ":stop":
            state["status"] = "SAFETY_STOP"; state["end_reason"] = "相手役が会話の終了を望んだため停止しました。"
            save_state(state); render_html(state); return 0
        result = client.post(f"/api/matches/{match_id}/messages", json={"role": "them", "body": partner_reply})
        if result.status_code != 201:
            raise RuntimeError("相手役の返答をSQLiteへ保存できませんでした")
        previous = state["messages"][-1]["body"]
        send_partner_message(state, partner_reply)
        if has_concrete_meeting_agreement(previous, partner_reply):
            state["pending_meeting_confirmation"] = {"proposal": previous, "acceptance": partner_reply}
        save_state(state)
    elif partner_reply:
        raise SystemExit("相手の返信は、直前にアプリ側が送信した後にのみ登録できます")

    if confirm_success:
        try:
            confirm_meeting_success(state)
        except (ValueError, KeyError) as exc:
            raise SystemExit(str(exc))
        save_state(state); render_html(state)
        print("SUCCESS: 保存済みの日時・場所提案と相手の承諾を確認しました。")
        return 0
    if state.get("pending_meeting_confirmation"):
        print("具体的な約束の候補を検出しました。発言を人が確認し、明確な合意なら --resume --confirm-success を指定してください。")
        save_state(state); render_html(state); return 0

    if state["messages"] and state["messages"][-1]["speaker"] == "app":
        print("直前のアプリ側送信に対する相手役の返答待ちです。再生成は行いません。")
        save_state(state); render_html(state); return 0

    if not can_send_app(state):
        state["status"] = "LIMIT_REACHED"; state["end_reason"] = "アプリ側の送信上限20通に達しました。21通目は生成していません。"
        save_state(state); render_html(state); return 0

    if state.get("pending_generation"):
        pending = state["pending_generation"]
    else:
        settings = {"mode": "reply", "match_id": match_id, "count": 3, "tone": "自動",
                    "direction": direction, "extra": extra, "show_policy": True}
        index = next((i for i,pair in enumerate(MODEL_ORDER) if pair == (state.get("last_account"), state.get("last_model"))), 0)
        if state["api_requests"] and not state["api_requests"][-1]["ok"]:
            last = state["api_requests"][-1]
            index = next((i for i,pair in enumerate(MODEL_ORDER) if pair == (last["account_alias"], last["model"])), 0)
        pending = None
        while index < len(MODEL_ORDER):
            account, model = MODEL_ORDER[index]
            os.environ["GEMINI_API_KEY"] = keys[account]
            os.environ["GEMINI_MODEL"] = model
            if state["api_requests"]:
                time.sleep(4.1)
            response = client.post("/api/generate", json=settings)
            req = {"request_number": len(state["api_requests"])+1, "at": utc_now(), "account_alias": account,
                   "model": model, "ok": response.status_code == 200, "app_http_status": response.status_code}
            if response.status_code != 200:
                detail = response.json().get("detail", "")
                limited = "レート制限" in detail or "利用枠" in detail
                req["error_type"] = "rate_limit" if limited else "authentication_model_or_connection"
                state["api_requests"].append(req); save_state(state)
                next_index = fallback_slot(limited, index)
                if next_index is None:
                    state["status"] = "BLOCKED"
                    state["end_reason"] = f"Gemini通信が{req['error_type']}で失敗しました。アプリの安全な説明: {detail}"
                    save_state(state); render_html(state)
                    print(f"BLOCKED: app endpoint HTTP {response.status_code}; {req['error_type']}。秘密値/SDK詳細は出力していません。")
                    return 2
                index = next_index
                continue
            data = response.json()
            candidates = [data["recommended"], *data["alternatives"]]
            req["candidate_count"] = len(candidates); req["demo"] = data.get("demo")
            state["api_requests"].append(req); save_state(state)
            if data.get("demo") is not False or len(candidates) != 3:
                state["status"] = "BLOCKED"; state["end_reason"] = "デモ応答または候補数不一致を検出しました。"
                save_state(state); render_html(state); return 2
            pending = {"account": account, "model": model, "data": data, "candidates": candidates, "settings": settings}
            state["pending_generation"] = pending
            state["last_account"] = account; state["last_model"] = model
            save_state(state); break
    account, model = pending["account"], pending["model"]
    data, candidates, settings = pending["data"], pending["candidates"], pending["settings"]
    print(f"Gemini実応答: {model} / 候補3案")
    for i,candidate in enumerate(candidates, 1):
        print(f"{i}. [{candidate['label']}] {candidate['text']}")
    print(f"理由: {data.get('reason')} / 会話方針: {data.get('strategy','')}")
    if candidate_number is None:
        print("生成結果をJSONにも保存しました。次に --resume --candidate-number 1|2|3 で候補を選びます。")
        save_state(state); render_html(state); return 0
    if candidate_number not in (1,2,3):
        raise SystemExit("候補番号は1・2・3です")
    selected = candidates[candidate_number-1]
    selection_reason = "推奨候補" if candidate_number == 1 else "選択した代替候補。選択理由は会話分析に記録する。"
    result = client.post(f"/api/matches/{match_id}/messages", json={"role": "me", "body": selected["text"]})
    if result.status_code != 201:
        state["status"] = "BLOCKED"; state["end_reason"] = "選択候補をSQLiteへ保存できませんでした。"
        save_state(state); render_html(state); return 2
    turn = {"turn_number": len(state["turns"])+1, "model": model, "account_alias": account,
            "api_status": "success", "candidates": candidates, "recommended": data["recommended"],
            "reason": data.get("reason"), "strategy": data.get("strategy"), "settings": settings,
            "selection_reason": selection_reason, "api_request_number": len(state["api_requests"])}
    send_app_message(state, selected["text"], turn)
    state.pop("pending_generation", None)
    if state["app_sent_count"] == MAX_APP_MESSAGES:
        state["status"] = "LIMIT_REACHED"; state["end_reason"] = "アプリ側20通を送信。21通目は生成・送信しません。"
    save_state(state); render_html(state)
    print(f"選択した候補をSQLiteへ保存: アプリ側{state['app_sent_count']}通目")
    if state["status"] == "LIMIT_REACHED":
        return 0
    print("相手役の返答を作成後、--resume --partner-reply に渡してください。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-dir", type=Path, default=Path(os.environ.get("MRA_API_DIR", "API")),
                        help="ユーザーが指定したローカルAPI認証ファイルのフォルダー（値は出力しません）")
    parser.add_argument("--opening-message", help="架空の相手役による開始文（新規実験のみ）")
    parser.add_argument("--resume", action="store_true", help="保存済みのBLOCKED/RUNNING実験を再開")
    parser.add_argument("--candidate-number", type=int, choices=(1,2,3), help="保存済みのGemini候補から送信する番号")
    parser.add_argument("--partner-reply", help="実際の履歴を読んだCodex相手役の返信。未生成候補は参照しない")
    parser.add_argument("--confirm-success", action="store_true", help="保存済みの日時・場所と相手の明確な承諾を確認した後に成功判定")
    parser.add_argument("--direction", default="自然に会話を広げる", help="Geminiの返信方向設定")
    parser.add_argument("--extra", default="", help="追加指示。原則空欄")
    args = parser.parse_args()
    return main_run(args.api_dir, args.opening_message, args.resume, args.candidate_number,
                    args.partner_reply, args.direction, args.extra, args.confirm_success)


if __name__ == "__main__":
    raise SystemExit(main())
