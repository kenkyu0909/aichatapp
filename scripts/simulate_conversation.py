"""Run a fictional, resumable conversation through the existing FastAPI app."""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sqlite3
import sys
import tempfile
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
SELF_002 = {
    "name": "高橋ゆう", "age": 27, "region": "神奈川県横浜市", "occupation": "出版社の営業",
    "hobbies": ["読書", "喫茶店", "散歩"], "food": ["カレー", "パスタ"],
    "available_area": "横浜駅・みなとみらい周辺", "availability": "10月下旬の土曜午後",
    "profile": "横浜で出版社の営業をしています。休日は本屋や喫茶店をのんびり巡ることが多いです。カレーとパスタが好きです。まずは自然にお話しできたらうれしいです。",
    "avoid": "根拠のない共通点、大げさな褒め言葉、質問攻め、返信の催促。",
}
PARTNER_002_PUBLIC = {
    "name": "森さやか", "age": 26, "region": "神奈川県川崎市", "occupation": "図書館司書",
    "hobbies": ["カフェ", "映画", "街歩き"], "food": ["焼き菓子", "オムライス"],
    "profile": "川崎で図書館司書をしています。休日は気になるカフェで本を読んだり、映画を観たりしています。焼き菓子とオムライスが好きです。ゆっくり話せる方だとうれしいです。",
    "conversation_style": "落ち着いていて自然な会話。質問攻めや急な誘いには慎重。",
}
PARTNER_002_INTERNAL = (
    "Codexだけが見る架空の人物設定。相手の発言と公開プロフィールに沿って自然に返す。"
    "短文や質問を返さない返事もする。会うことには慎重だが、会話が自然なら検討する。"
    "実験の成功条件を理由に承諾しない。"
)


def experiment_paths(experiment_id: str) -> tuple[Path, Path, Path]:
    if not re.fullmatch(r"conversation_[0-9]{3}", experiment_id):
        raise ValueError("実験IDはconversation_と3桁の数字で指定してください")
    if experiment_id == "conversation_001":
        return JSON_FILE, HTML_FILE, DATA_DIR
    return (
        SIM_DIR / f"{experiment_id}.json",
        SIM_DIR / f"{experiment_id}.html",
        Path(tempfile.gettempdir()) / f"mra-{experiment_id.replace('_', '-')}-sandbox",
    )


def people_for(experiment_id: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    if experiment_id == "conversation_002":
        return SELF_002, PARTNER_002_PUBLIC, PARTNER_002_INTERNAL
    if experiment_id == "conversation_001":
        return SELF, PARTNER_PUBLIC, PARTNER_INTERNAL
    raise ValueError("未定義の実験IDです")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_state(experiment_id: str = "conversation_001") -> dict[str, Any]:
    self_profile, partner_public, partner_internal = people_for(experiment_id)
    return {
        "schema_version": 1, "experiment_id": experiment_id, "started_at": utc_now(),
        "updated_at": utc_now(), "status": "RUNNING", "end_reason": None,
        "people": {"app_user": self_profile, "partner_public": partner_public, "partner_internal": partner_internal},
        "environment": {"os": "Windows", "browser_for_report": "Firefox", "database": "架空データ専用の一時SQLite"},
        "api_requests": [], "messages": [], "turns": [], "app_sent_count": 0,
        "partner_sent_count": 0, "first_invite_app_message": None, "meeting_agreement": None,
        "assessment": {},
    }


def save_state(state: dict[str, Any], path: Path | None = None) -> None:
    path = path or JSON_FILE
    state["updated_at"] = utc_now()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def save_experiment_state(state: dict[str, Any]) -> None:
    json_path, _, _ = experiment_paths(state.get("experiment_id", "conversation_001"))
    save_state(state, json_path)


def render_experiment(state: dict[str, Any]) -> None:
    _, html_path, _ = experiment_paths(state.get("experiment_id", "conversation_001"))
    render_html(state, html_path)


def export_profiles(path: Path | None = None, experiment_id: str = "conversation_001") -> None:
    self_profile, partner, internal = people_for(experiment_id)
    path = path or (PROFILE_FILE if experiment_id == "conversation_001" else SIM_DIR / f"profiles_{experiment_id[-3:]}.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# 会話シミュレーション用の架空プロフィール\n\n実験ID: `{experiment_id}`（2026-10-14）\n\n"
        "## アプリ側（本人役）\n\n"
        f"- 名前・年齢: {self_profile['name']}、{self_profile['age']}歳\n- 居住地・仕事: {self_profile['region']}、{self_profile['occupation']}\n"
        f"- 趣味: {', '.join(self_profile['hobbies'])}\n- 公開プロフィール: {self_profile['profile']}\n- 避けたい表現: {self_profile['avoid']}\n\n"
        "## 相手役の公開プロフィール（アプリ/Geminiに渡す情報）\n\n"
        f"- 名前・年齢: {partner['name']}、{partner['age']}歳\n"
        f"- 居住地・仕事: {partner['region']}、{partner['occupation']}\n"
        f"- 趣味: {', '.join(partner['hobbies'])}\n- 公開プロフィール: {partner['profile']}\n"
        f"- 会話スタイル: {partner['conversation_style']}\n\n"
        "## 相手役の内部設定（Codexのみ。アプリ/Geminiには送信しない）\n\n"
        f"{internal}\n", encoding="utf-8",
    )


def can_send_app(state: dict[str, Any]) -> bool:
    return state["status"] == "RUNNING" and state["app_sent_count"] < MAX_APP_MESSAGES


def can_receive_partner(state: dict[str, Any]) -> bool:
    return state["status"] == "RUNNING" and bool(state.get("messages")) and state["messages"][-1]["speaker"] == "app"


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


def api_request_record(data: dict[str, Any], request_number: int, http_status: int) -> dict[str, Any]:
    """Record only the backend's actual selection; the harness never rotates keys/models."""
    attempted = data.get("attempted_models", [])
    attempted = [
        {"api_alias": item["api_alias"], "model": item["model"]}
        for item in attempted[:4]
        if isinstance(item, dict)
        and item.get("api_alias") in ("API1", "API2")
        and isinstance(item.get("model"), str)
    ] if isinstance(attempted, list) else []
    detail = data.get("detail")
    if isinstance(detail, str):
        detail = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "[秘匿]", detail)
        detail = re.sub(r"(?i)(api[_ -]?key|authorization)\s*[:=]\s*\S+", r"\1=[秘匿]", detail)
        detail = detail[:500]
    else:
        detail = None
    result = {
        "request_number": request_number,
        "ok": http_status == 200,
        "api_alias": data.get("api_alias"),
        "model": data.get("model"),
        "attempt_count": data.get("api_attempt_count"),
        "attempted_models": attempted,
        "error_code": data.get("error_code"),
        "app_http_status": http_status,
    }
    if detail is not None:
        result["detail"] = detail
    return result


INVITE_PATTERN = re.compile(r"(行きませんか|行かない|会いませんか|一緒に.{0,12}(行|会)|ご飯|食事|カフェ|喫茶店|ランチ|散歩).{0,30}(行|会|どう|ません|いい)|今度.{0,20}(会|行)")
POSITIVE_PATTERN = re.compile(r"(いいですね|大丈夫|ぜひ|行きましょう|お願いします|楽しみです|問題ない|行けます|空いてます)")
NEGATIVE_PATTERN = re.compile(r"(難しい|無理|行けません|ごめんなさい|やめて|会いたくない|また今度|まだ分からない|まだわからない|後で|あとで|未定|もし|都合が合えば|予定が分からない|予定がわからない|控えたい|連絡しないで|やり取りを終|返信を控)")
DATE_PATTERN = re.compile(r"(月|火|水|木|金|土|日)曜|\d{1,2}月\d{1,2}日")
TIME_PATTERN = re.compile(r"(午前|午後)?\s*\d{1,2}時|\d{1,2}:\d{2}")
PLACE_PATTERN = re.compile(r"(駅|カフェ|喫茶店|レストラン|店|公園|美術館|丁目|エリア)")


def is_partner_refusal(body: str) -> bool:
    return bool(re.search(
        r"(これ以上.{0,10}(やり取り|連絡|会話).{0,20}(控え|したく|やめ)|"
        r"(今後|これ以上).{0,15}(やり取り|連絡|会話).{0,20}(控え|終わり|やめ)|"
        r"(やり取り|連絡|会話).{0,20}(控えたい|控えさせ|したくない|終わりにしたい|やめたい)|"
        r"(やり取り|メッセージ|連絡|会話).{0,20}(控えさせ|控えたい|控えます)|"
        r"もう.{0,8}(やり取り|連絡|会話).{0,8}(しません|したくない)|"
        r"(もう|今後).{0,8}(連絡しないで|会わないで)|会いたくない)",
        body,
    ))


def find_meeting_agreement(messages: list[dict[str, Any]]) -> dict[str, str] | None:
    """Find a concrete plan accumulated across app turns and explicitly accepted by partner."""
    app_plan: list[str] = []
    invite_started = False
    for message in messages:
        body = str(message.get("body", ""))
        if message.get("speaker") == "app":
            if INVITE_PATTERN.search(body):
                invite_started = True
            if invite_started:
                app_plan.append(body)
            continue
        if not invite_started:
            continue
        combined = " ".join(app_plan)
        if (POSITIVE_PATTERN.search(body) and not NEGATIVE_PATTERN.search(body)
                and DATE_PATTERN.search(combined) and TIME_PATTERN.search(combined) and PLACE_PATTERN.search(combined)):
            return {"proposal": combined, "acceptance": body}
        # Keep an invitation open while the plan is being negotiated. A refusal ends its context.
        if is_partner_refusal(body):
            app_plan = []
            invite_started = False
    return None


def has_concrete_meeting_agreement(app_proposal: str, partner_reply: str) -> bool:
    return bool(POSITIVE_PATTERN.search(partner_reply) and not NEGATIVE_PATTERN.search(partner_reply)
                and DATE_PATTERN.search(app_proposal) and TIME_PATTERN.search(app_proposal)
                and PLACE_PATTERN.search(app_proposal))


def prepare_meeting_confirmation(state: dict[str, Any]) -> None:
    state["pending_meeting_confirmation"] = find_meeting_agreement(state.get("messages", []))


def confirm_meeting_success(state: dict[str, Any]) -> None:
    """Finalize SUCCESS only after an explicit operator review of saved utterances."""
    if state.get("status") == "SAFETY_STOP" or (state.get("messages") and
            state["messages"][-1].get("speaker") == "partner" and
            is_partner_refusal(state["messages"][-1].get("body", ""))):
        raise ValueError("安全停止が優先されるためSUCCESSに変更できません")
    if state.get("status") not in ("RUNNING", "BLOCKED"):
        raise ValueError("実験が終了状態のためSUCCESSに変更できません")
    pending = find_meeting_agreement(state.get("messages", []))
    recorded = state.get("pending_meeting_confirmation")
    if not pending or not recorded or pending != recorded:
        raise ValueError("日時・場所を含む提案と明確な相手の承諾を確認できません")
    state["status"] = "SUCCESS"
    state["meeting_agreement"] = {"proposal": pending["proposal"], "acceptance": pending["acceptance"]}
    state["end_reason"] = "評価者が保存済みの発言を確認し、具体的な日時・場所と相手の明確な承諾を確認しました。"
    for message in state["messages"]:
        if message.get("speaker") == "partner" and message.get("body") == pending["acceptance"]:
            message["meeting_agreement"] = True
    # The proposal is recorded as a combined string when details span multiple turns.
    for message in state["messages"]:
        if message.get("speaker") == "app" and message.get("body") and message["body"] in pending["proposal"]:
            message["meeting_agreement"] = True


def finalize_after_partner_reply(state: dict[str, Any]) -> None:
    """Resolve refusal/agreement/limit only after the partner's utterance is saved."""
    if not state.get("messages") or state["messages"][-1].get("speaker") != "partner":
        raise RuntimeError("終了判定には保存済みの相手発言が必要です")
    latest = state["messages"][-1]["body"]
    if is_partner_refusal(latest):
        state["status"] = "SAFETY_STOP"
        state["end_reason"] = "相手役がこれ以上のやり取りを望まないと伝えたため停止しました。"
        return
    prepare_meeting_confirmation(state)
    if state.get("pending_meeting_confirmation"):
        return
    if state["app_sent_count"] >= MAX_APP_MESSAGES:
        state["status"] = "LIMIT_REACHED"
        state["end_reason"] = "20通目への相手の返信を確認しました。会う約束は成立せず、21通目は生成・送信していません。"


def render_html(state: dict[str, Any], path: Path | None = None) -> None:
    path = path or HTML_FILE
    e = lambda value: html.escape(str(value if value is not None else ""), quote=True)
    labels = {"SUCCESS": "会う約束が成立", "LIMIT_REACHED": "送信上限到達", "SAFETY_STOP": "安全上の停止", "BLOCKED": "技術的に中断", "AWAITING_USER_INFO": "本人情報の回答待ち", "RUNNING": "実験中"}
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


def import_app(data_dir: Path):
    os.environ["APP_DATA_DIR"] = str(data_dir)
    sys.path.insert(0, str(ROOT))
    import importlib
    from fastapi.testclient import TestClient
    if "app" in sys.modules:
        backend = importlib.reload(sys.modules["app"])
    else:
        import app as backend
    return TestClient(backend.app)


def db_matches_state(client: Any, state: dict[str, Any]) -> bool:
    response = client.get(f"/api/matches/{state['match_id']}/messages")
    if response.status_code != 200:
        return False
    expected = [("me" if m["speaker"] == "app" else "them", m["body"]) for m in state["messages"]]
    return [(m["role"], m["body"]) for m in response.json()] == expected


def restore_state_to_empty_db(client: Any, state: dict[str, Any]) -> dict[str, Any]:
    """Restore fictional experiment state using normal app endpoints, refusing nonempty DBs."""
    validate_restore_state(state)
    client.get("/api/profile")  # Initializes the empty schema before the transaction begins.
    backend = sys.modules.get("app")
    if backend is None:
        raise RuntimeError("アプリのSQLite接続を確認できません")
    try:
        with backend.database() as db:
            db.execute("BEGIN IMMEDIATE")
            profile = db.execute("SELECT content,avoid FROM profile WHERE id=1").fetchone()
            match_count = db.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
            message_count = db.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            if not profile or profile["content"] or profile["avoid"] or match_count or message_count:
                raise RuntimeError("復元先は空の実験用SQLiteではありません。既存データを変更せず停止しました")
            person = state["people"]["app_user"]
            partner = state["people"]["partner_public"]
            db.execute("UPDATE profile SET content=?,avoid=? WHERE id=1", (person.get("profile", ""), person.get("avoid", "")))
            cursor = db.execute("INSERT INTO matches(name,description) VALUES (?,?)", (partner["name"], partner.get("profile", "")))
            new_match_id = cursor.lastrowid
            for message in state["messages"]:
                role = "me" if message["speaker"] == "app" else "them"
                db.execute("INSERT INTO messages(match_id,role,body) VALUES (?,?,?)", (new_match_id, role, message["body"]))
            restored_profile = db.execute("SELECT content,avoid FROM profile WHERE id=1").fetchone()
            restored_match = db.execute("SELECT name,description FROM matches WHERE id=?", (new_match_id,)).fetchone()
            restored_messages = db.execute(
                "SELECT role,body FROM messages WHERE match_id=? ORDER BY id", (new_match_id,)
            ).fetchall()
            expected_messages = [
                ("me" if message["speaker"] == "app" else "them", message["body"])
                for message in state["messages"]
            ]
            if (not restored_profile or
                    (restored_profile["content"], restored_profile["avoid"]) !=
                    (person.get("profile", ""), person.get("avoid", "")) or
                    not restored_match or
                    (restored_match["name"], restored_match["description"]) !=
                    (partner["name"], partner.get("profile", "")) or
                    [(row["role"], row["body"]) for row in restored_messages] != expected_messages):
                raise RuntimeError("トランザクション内の整合性確認に失敗し、復元をロールバックしました")
    except sqlite3.Error as exc:
        raise RuntimeError("JSON復元トランザクションに失敗し、全変更をロールバックしました") from exc
    restored = dict(state)
    restored["match_id"] = new_match_id
    if not db_matches_state(client, restored):
        raise RuntimeError("トランザクション後のSQLiteとJSON会話履歴が一致しません")
    return restored


def validate_restore_state(state: Any) -> None:
    """Validate every restored profile/message before making any database change."""
    try:
        if not isinstance(state, dict) or not re.fullmatch(r"conversation_[0-9]{3}", str(state.get("experiment_id", ""))):
            raise ValueError
        people_for(state["experiment_id"])
        people = state["people"]
        user, partner = people["app_user"], people["partner_public"]
        if not isinstance(user, dict) or not isinstance(partner, dict):
            raise ValueError
        if not isinstance(user.get("profile", ""), str) or len(user.get("profile", "")) > 12000:
            raise ValueError
        if not isinstance(user.get("avoid", ""), str) or len(user.get("avoid", "")) > 4000:
            raise ValueError
        if not isinstance(partner.get("name"), str) or not 1 <= len(partner["name"].strip()) <= 100:
            raise ValueError
        if not isinstance(partner.get("profile", ""), str) or len(partner.get("profile", "")) > 12000:
            raise ValueError
        messages = state.get("messages")
        if not isinstance(messages, list):
            raise ValueError
        if len(messages) > MAX_APP_MESSAGES * 2 + 1:
            raise ValueError
        app_count = partner_count = 0
        for index, message in enumerate(messages, 1):
            if not isinstance(message, dict) or message.get("speaker") not in ("app", "partner"):
                raise ValueError
            if message.get("sequence") != index:
                raise ValueError
            body = message.get("body")
            if not isinstance(body, str) or not body.strip() or len(body) > 12000:
                raise ValueError
            app_count += message["speaker"] == "app"
            partner_count += message["speaker"] == "partner"
            if message["speaker"] == "app" and message.get("app_send_number") != app_count:
                raise ValueError
        if state.get("app_sent_count", 0) != app_count or app_count > MAX_APP_MESSAGES:
            raise ValueError
        if state.get("partner_sent_count", 0) != partner_count:
            raise ValueError
        turns = state.get("turns", [])
        requests = state.get("api_requests", [])
        if not isinstance(turns, list) or len(turns) != app_count or not isinstance(requests, list):
            raise ValueError
        for request_number, request in enumerate(requests, 1):
            if not isinstance(request, dict) or request.get("request_number") != request_number or not isinstance(request.get("ok"), bool):
                raise ValueError
            attempts = request.get("attempt_count")
            minimum_attempts = 0 if request.get("result_type") in ("needs_user_info", "generation_blocked") else 1
            if attempts is not None and (not isinstance(attempts, int) or not minimum_attempts <= attempts <= 4):
                raise ValueError
            attempted_models = request.get("attempted_models", [])
            if not isinstance(attempted_models, list) or len(attempted_models) > 4:
                raise ValueError
            for attempted in attempted_models:
                if (not isinstance(attempted, dict) or attempted.get("api_alias") not in ("API1", "API2")
                        or not isinstance(attempted.get("model"), str)):
                    raise ValueError
            if request.get("detail") is not None and (not isinstance(request["detail"], str) or len(request["detail"]) > 500):
                raise ValueError
            for field in ("api_alias", "model"):
                if request.get(field) is not None and not isinstance(request[field], str):
                    raise ValueError
        for turn in turns:
            if not isinstance(turn, dict) or not isinstance(turn.get("candidates", []), list):
                raise ValueError
            for candidate in turn.get("candidates", []):
                if not isinstance(candidate, dict) or not isinstance(candidate.get("text"), str):
                    raise ValueError
        pending = state.get("pending_generation")
        if pending is not None:
            if not isinstance(pending, dict) or not all(key in pending for key in ("account", "model", "data", "candidates", "settings")):
                raise ValueError
            if not isinstance(pending["data"], dict) or not isinstance(pending["settings"], dict) or not isinstance(pending["candidates"], list):
                raise ValueError
            for candidate in pending["candidates"]:
                if not isinstance(candidate, dict) or not isinstance(candidate.get("text"), str):
                    raise ValueError
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ValueError("復元用JSON全体の形式または値が不正です。DBは変更していません") from None


def generation_settings(match_id: int, direction: str, extra: str, mode: str = "reply") -> dict[str, Any]:
    if mode not in {"first", "reply", "followup"}:
        raise ValueError("実験で使用できない生成モードです")
    return {"mode": mode, "match_id": match_id, "count": 3, "tone": "自動",
            "direction": direction, "extra": extra, "show_policy": True, "response_version": 2}


def call_generate_once(client: Any, settings: dict[str, Any], state: dict[str, Any],
                       json_path: Path | None = None, html_path: Path | None = None) -> tuple[Any, dict[str, Any], dict[str, Any]] | None:
    """Call once; ambiguous transport/JSON failures are persisted and never auto-replayed."""
    default_json, default_html, _ = experiment_paths(state.get("experiment_id", "conversation_001"))
    json_path = json_path or default_json
    html_path = html_path or default_html
    request_number = len(state["api_requests"]) + 1
    response = None
    status_code = 0
    try:
        response = client.post("/api/generate", json=settings)
        status_code = int(response.status_code)
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("response is not a JSON object")
    except Exception as exc:
        invalid_json = response is not None
        detail = ("Gemini応答をJSONとして読み取れませんでした。再送信前に状態を確認してください。"
                  if invalid_json else "Geminiへの通信結果を確認できませんでした。重複送信を避けるため自動再試行を停止しました。")
        record = api_request_record({"detail": detail}, request_number, status_code)
        record.update({
            "ok": False,
            "error_type": "invalid_json" if invalid_json else "transport_error",
            "error_class": type(exc).__name__,
            "generation_uncertain": True,
            "at": utc_now(),
        })
        state["api_requests"].append(record)
        state["status"] = "BLOCKED"
        state["generation_uncertain"] = True
        state["uncertain_generation_settings"] = settings
        state["end_reason"] = detail
        save_state(state, json_path)
        render_html(state, html_path)
        return None
    return response, data, api_request_record(data, request_number, status_code)


def allow_uncertain_generation_retry(state: dict[str, Any], explicitly_authorized: bool = False) -> bool:
    return not state.get("generation_uncertain", False) or explicitly_authorized


def pause_for_user_info(state: dict[str, Any], data: dict[str, Any], settings: dict[str, Any], request_number: int) -> None:
    questions = data.get("user_questions")
    if not data.get("needs_user_info") or not isinstance(questions, list) or not 1 <= len(questions) <= 3:
        raise ValueError("本人情報の確認応答が不正です")
    for item in questions:
        if not isinstance(item, dict) or not isinstance(item.get("question"), str) or not item["question"].strip():
            raise ValueError("本人への質問が不正です")
    if data.get("recommended") is not None or data.get("alternatives"):
        raise ValueError("本人情報の確認応答に送信候補が混在しています")
    state["status"] = "AWAITING_USER_INFO"
    state["end_reason"] = "本人情報の回答待ちです。未確認の事実を使った返信は生成していません。"
    state["pending_user_info"] = {
        "questions": questions,
        "reason": data.get("user_info_reason", "本人情報を確認する必要があります。"),
        "settings": settings,
        "api_request_number": request_number,
    }


def resume_user_info_settings(state: dict[str, Any], answers: list[str], skip: bool) -> dict[str, Any] | None:
    pending = state.get("pending_user_info")
    if not pending:
        raise ValueError("回答待ちの本人情報質問がありません")
    if not answers and not skip:
        return None
    questions = pending["questions"]
    if skip:
        if answers:
            raise ValueError("スキップと回答は同時に指定できません")
        state["skipped_user_info"] = True
        previous = state.get("user_info_answers", [])
        settings = dict(pending["settings"], user_answers=previous, skipped_user_info=True)
    else:
        if len(answers) != len(questions):
            raise ValueError(f"質問は{len(questions)}件あります。同じ件数の --user-answer を指定してください")
        if any(not isinstance(answer, str) or not answer.strip() or len(answer) > 1000 for answer in answers):
            raise ValueError("回答は空欄にせず、1000文字以内で入力してください")
        new_answers = [
            {"question": item["question"], "answer": answer.strip()}
            for item, answer in zip(questions, answers, strict=True)
        ]
        previous = state.get("user_info_answers", [])
        state["user_info_answers"] = previous + new_answers
        state["skipped_user_info"] = False
        settings = dict(pending["settings"], user_answers=state["user_info_answers"], skipped_user_info=False)
    state.pop("pending_user_info", None)
    state["status"] = "RUNNING"
    state["end_reason"] = None
    return settings


def main_run(opening: str | None, resume: bool,
             candidate_number: int | None, partner_reply: str | None,
             direction: str, extra: str, confirm_success: bool,
             user_answers: list[str] | None = None, skip_user_info: bool = False,
             retry_uncertain_generation: bool = False,
             experiment_id: str = "conversation_001", initial_mode: str = "reply") -> int:
    json_path, html_path, data_dir = experiment_paths(experiment_id)
    if initial_mode not in {"first", "reply"}:
        raise SystemExit("初回モードはfirstまたはreplyです")
    self_profile, partner_public, _ = people_for(experiment_id)
    if json_path.exists() and not resume:
        raise SystemExit("会話JSONが既にあります。既存結果を上書きしないため --resume を使ってください")
    if resume and not json_path.is_file():
        raise SystemExit("再開用のJSONログがありません")
    export_profiles(experiment_id=experiment_id)
    state = json.loads(json_path.read_text(encoding="utf-8")) if resume else new_state(experiment_id)
    if not resume:
        state["initial_mode"] = initial_mode
    else:
        initial_mode = state.get("initial_mode", initial_mode)
    if not resume and data_dir.exists():
        raise SystemExit("専用SQLite保存先が存在します。内容を削除せず停止しました")
    data_dir.mkdir(parents=True, exist_ok=True)
    client = import_app(data_dir)
    resumed_user_settings = None
    if resume:
        if state.get("status") not in ("RUNNING", "BLOCKED", "AWAITING_USER_INFO") or state.get("experiment_id") != experiment_id:
            raise SystemExit("実験状態が再開可能な状態ではありません")
        if not db_matches_state(client, state):
            state = restore_state_to_empty_db(client, state)
        if state.get("generation_uncertain"):
            if not allow_uncertain_generation_retry(state, retry_uncertain_generation):
                print("前回のGeminiリクエストは応答を確認できていません。重複生成を避けるため停止中です。状態を確認し、明示的に再試行する場合だけ --retry-uncertain-generation を指定してください。")
                save_experiment_state(state); render_experiment(state); return 2
            resumed_user_settings = state.pop("uncertain_generation_settings", None)
            state.pop("generation_uncertain", None)
        elif retry_uncertain_generation:
            raise SystemExit("不確実な生成リクエストがないため再試行指定を使えません")
        if state.get("pending_user_info"):
            resumed_user_settings = resume_user_info_settings(
                state, user_answers or [], skip=skip_user_info
            )
            if resumed_user_settings is None:
                print("本人情報の回答待ちです。保存済み質問に --user-answer を指定してください。スキップする場合は --skip-user-info を指定できます。")
                for question in state["pending_user_info"]["questions"]:
                    print(f"- {question['question']}（{question.get('purpose', '')}）")
                save_experiment_state(state); render_experiment(state); return 0
        elif state.get("status") == "AWAITING_USER_INFO":
            raise SystemExit("回答待ち状態ですが質問情報がありません。JSONを変更せず停止しました")
        elif user_answers or skip_user_info:
            raise SystemExit("回答待ちの本人情報質問がありません")
        state["status"] = "RUNNING"; state["end_reason"] = None
    elif retry_uncertain_generation or user_answers or skip_user_info:
        raise SystemExit("回答・不確実な生成の再試行には --resume が必要です")
    else:
        client.put("/api/profile", json={"content": self_profile["profile"], "avoid": self_profile["avoid"]})
        created = client.post("/api/matches", json={"name": partner_public["name"], "description": partner_public["profile"]})
        if created.status_code != 201:
            raise RuntimeError("架空プロフィールの登録に失敗しました")
        state["match_id"] = created.json()["id"]
    match_id = state["match_id"]

    if not state["messages"] and not (not resume and initial_mode == "first"):
        if not opening:
            print("架空の相手役の開始メッセージを --opening-message で渡してください")
            state["end_reason"] = "開始メッセージ入力待ちです。"
            save_experiment_state(state); render_experiment(state); return 0
        result = client.post(f"/api/matches/{match_id}/messages", json={"role": "them", "body": opening})
        if result.status_code != 201:
            raise RuntimeError("開始メッセージをSQLiteへ保存できませんでした")
        send_partner_message(state, opening); save_experiment_state(state)

    if can_receive_partner(state) and partner_reply:
        result = client.post(f"/api/matches/{match_id}/messages", json={"role": "them", "body": partner_reply})
        if result.status_code != 201:
            raise RuntimeError("相手役の返答をSQLiteへ保存できませんでした")
        send_partner_message(state, partner_reply)
        finalize_after_partner_reply(state)
        save_experiment_state(state)
    elif partner_reply:
        raise SystemExit("相手の返信は、直前にアプリ側が送信した後にのみ登録できます")

    if confirm_success:
        try:
            confirm_meeting_success(state)
        except (ValueError, KeyError) as exc:
            raise SystemExit(str(exc))
        save_experiment_state(state); render_experiment(state)
        print("SUCCESS: 保存済みの日時・場所提案と相手の承諾を確認しました。")
        return 0
    if state.get("pending_meeting_confirmation"):
        print("具体的な約束の候補を検出しました。発言を人が確認し、明確な合意なら --resume --confirm-success を指定してください。")
        save_experiment_state(state); render_experiment(state); return 0

    if state["status"] in ("SAFETY_STOP", "LIMIT_REACHED"):
        save_experiment_state(state); render_experiment(state)
        print(f"{state['status']}: {state.get('end_reason')}")
        return 0

    if state["messages"] and state["messages"][-1]["speaker"] == "app":
        print("直前のアプリ側送信に対する相手役の返答待ちです。再生成は行いません。")
        save_experiment_state(state); render_experiment(state); return 0

    if not can_send_app(state):
        state["status"] = "LIMIT_REACHED"; state["end_reason"] = "アプリ側の送信上限20通に達しました。21通目は生成していません。"
        save_experiment_state(state); render_experiment(state); return 0

    if state.get("pending_generation"):
        pending = state["pending_generation"]
    else:
        mode = "first" if not state["messages"] and initial_mode == "first" else "reply"
        settings = resumed_user_settings or generation_settings(match_id, direction, extra, mode)
        result = call_generate_once(client, settings, state, json_path, html_path)
        if result is None:
            print("BLOCKED: Geminiの応答を安全に確認できず、JSONとHTMLに状態を保存しました。自動再試行していません。")
            return 2
        response, response_data, req = result
        req["at"] = utc_now()
        if response.status_code != 200:
            detail = req.get("detail") or "AI生成に失敗しました。"
            req["error_type"] = "rate_limit" if "レート制限" in detail or "利用枠" in detail else "generation_error"
            state["api_requests"].append(req); save_experiment_state(state)
            state["status"] = "BLOCKED"
            state["end_reason"] = f"/api/generate がHTTP {response.status_code}で失敗しました。アプリの安全な説明: {detail}"
            save_experiment_state(state); render_experiment(state)
            print(f"BLOCKED: app endpoint HTTP {response.status_code}; APIキーや内部例外の詳細は記録していません。")
            return 2
        if response_data.get("needs_user_info"):
            state["api_requests"].append(req)
            req["result_type"] = "needs_user_info"
            if req["attempt_count"] == 0:
                req["ok"] = True
            save_experiment_state(state)
            try:
                pause_for_user_info(state, response_data, settings, req["request_number"])
            except ValueError as exc:
                state["status"] = "BLOCKED"
                state["end_reason"] = "本人情報確認応答の形式を検証できませんでした。"
                save_experiment_state(state); render_experiment(state)
                print(f"BLOCKED: {exc}")
                return 2
            state.pop("uncertain_generation_settings", None)
            save_experiment_state(state); render_experiment(state)
            print(f"本人情報の回答待ちです。質問数: {len(state['pending_user_info']['questions'])}。送信数は増えていません。")
            for question in state["pending_user_info"]["questions"]:
                print(f"- {question['question']}（{question.get('purpose', '')}）")
            return 0
        if response_data.get("generation_blocked"):
            req["result_type"] = "generation_blocked"
            state["api_requests"].append(req)
            state["status"] = "BLOCKED"
            state["end_reason"] = response_data.get("blocking_reason") or "本人情報が不足しており、安全な候補を生成できませんでした。"
            state.pop("uncertain_generation_settings", None)
            save_experiment_state(state); render_experiment(state)
            print(f"BLOCKED: {state['end_reason']}")
            return 2
        if not isinstance(req["attempt_count"], int) or not 1 <= req["attempt_count"] <= 4:
            req["ok"] = False
            state["api_requests"].append(req)
            state["status"] = "BLOCKED"
            state["end_reason"] = "バックエンドのAPI試行回数が許容上限1〜4回の範囲外でした。"
            save_experiment_state(state); render_experiment(state)
            return 2
        if not req.get("api_alias") or not req.get("model"):
            req["ok"] = False
            state["api_requests"].append(req)
            state["status"] = "BLOCKED"
            state["end_reason"] = "/api/generate が実際に使用したAPI別名またはモデル名を返しませんでした。"
            save_experiment_state(state); render_experiment(state)
            return 2
        data = response_data
        try:
            candidates = [data["recommended"], *data["alternatives"]]
        except (KeyError, TypeError) as exc:
            state["api_requests"].append(req)
            state["status"] = "BLOCKED"
            state["end_reason"] = "Gemini応答に返信候補がなく、送信を停止しました。"
            save_experiment_state(state); render_experiment(state)
            print(f"BLOCKED: 応答形式エラー ({type(exc).__name__})")
            return 2
        req["candidate_count"] = len(candidates); req["demo"] = data.get("demo")
        state["api_requests"].append(req); save_experiment_state(state)
        if data.get("demo") is not False or len(candidates) != 3:
            state["status"] = "BLOCKED"; state["end_reason"] = "デモ応答または候補数不一致を検出しました。"
            save_experiment_state(state); render_experiment(state); return 2
        pending = {"account": req["api_alias"], "model": req["model"], "data": data,
                   "candidates": candidates, "settings": settings, "attempt_count": req["attempt_count"]}
        state["pending_generation"] = pending
        state.pop("uncertain_generation_settings", None)
        save_experiment_state(state)
    account, model = pending["account"], pending["model"]
    data, candidates, settings = pending["data"], pending["candidates"], pending["settings"]
    print(f"Gemini実応答: {model} / 候補3案")
    for i,candidate in enumerate(candidates, 1):
        print(f"{i}. [{candidate['label']}] {candidate['text']}")
    print(f"理由: {data.get('reason')} / 会話方針: {data.get('strategy','')}")
    if candidate_number is None:
        print("生成結果をJSONにも保存しました。次に --resume --candidate-number 1|2|3 で候補を選びます。")
        save_experiment_state(state); render_experiment(state); return 0
    if candidate_number not in (1,2,3):
        raise SystemExit("候補番号は1・2・3です")
    selected = candidates[candidate_number-1]
    selection_reason = "推奨候補" if candidate_number == 1 else "選択した代替候補。選択理由は会話分析に記録する。"
    result = client.post(f"/api/matches/{match_id}/messages", json={"role": "me", "body": selected["text"]})
    if result.status_code != 201:
        state["status"] = "BLOCKED"; state["end_reason"] = "選択候補をSQLiteへ保存できませんでした。"
        save_experiment_state(state); render_experiment(state); return 2
    turn = {"turn_number": len(state["turns"])+1, "model": model, "account_alias": account,
            "api_attempt_count": pending.get("attempt_count", 1),
            "api_status": "success", "candidates": candidates, "recommended": data["recommended"],
            "reason": data.get("reason"), "strategy": data.get("strategy"), "settings": settings,
            "selection_reason": selection_reason, "api_request_number": len(state["api_requests"])}
    send_app_message(state, selected["text"], turn)
    state.pop("pending_generation", None)
    save_experiment_state(state); render_experiment(state)
    print(f"選択した候補をSQLiteへ保存: アプリ側{state['app_sent_count']}通目")
    print("相手役の返答を作成後、--resume --partner-reply に渡してください。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--opening-message", help="架空の相手役による開始文（新規実験のみ）")
    parser.add_argument("--resume", action="store_true", help="保存済みのBLOCKED/RUNNING実験を再開")
    parser.add_argument("--candidate-number", type=int, choices=(1,2,3), help="保存済みのGemini候補から送信する番号")
    parser.add_argument("--partner-reply", help="実際の履歴を読んだCodex相手役の返信。未生成候補は参照しない")
    parser.add_argument("--user-answer", action="append", default=[], help="回答待ちの各質問への回答（質問ごとに指定）")
    parser.add_argument("--skip-user-info", action="store_true", help="本人情報の確認をスキップし、安全な代替返信だけを試す")
    parser.add_argument("--retry-uncertain-generation", action="store_true", help="応答不明だった生成を重複する可能性を理解した上で明示的に再試行")
    parser.add_argument("--confirm-success", action="store_true", help="保存済みの日時・場所と相手の明確な承諾を確認した後に成功判定")
    parser.add_argument("--direction", default="自然に会話を広げる", help="Geminiの返信方向設定")
    parser.add_argument("--extra", default="", help="追加指示。原則空欄")
    parser.add_argument("--experiment-id", default="conversation_001", help="保存先を分離する実験ID（例: conversation_002）")
    parser.add_argument("--initial-mode", choices=("first", "reply"), default="reply", help="空の履歴から始める場合の生成モード")
    args = parser.parse_args()
    return main_run(args.opening_message, args.resume, args.candidate_number,
                    args.partner_reply, args.direction, args.extra, args.confirm_success,
                    args.user_answer, args.skip_user_info, args.retry_uncertain_generation,
                    args.experiment_id, args.initial_mode)


if __name__ == "__main__":
    raise SystemExit(main())
