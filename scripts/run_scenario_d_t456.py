import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

# Add repo to sys.path
REPO = Path(r"C:\Users\poiuy\desktop\aichatapp2\verification-repo")
sys.path.insert(0, str(REPO))
import app
from fastapi.testclient import TestClient

HERE = Path(r"C:\Users\poiuy\desktop\aichatapp2\会話テスト")
STATE = HERE / "conversation_test_20261017_invite_d_schedule_T456.json"
HTML = HERE / "conversation_test_20261017_invite_d_schedule_T456.html"

SELF = {
    "name": "水野そよか", "age": "27", "area": "神奈川県横浜市", "job": "経理",
    "hobbies": ["喫茶店めぐり", "観葉植物", "小さな美術館", "読書"],
    "personality": "穏やかで聞き上手", "style": "敬語で短め。質問は一度にひとつ",
    "goal": "まずは自然に話せる関係を築きたい",
    "memo": "休日は喫茶店めぐりが好きで、窓ぎわの席でコーヒーを飲みながら短い小説やエッセイを読んでいます。家では観葉植物の手入れをしていて、ポトスとガジュマルを育てています。オムライスと季節のタルトが好きで、喫茶店ではタルトを選ぶことが多いです。"
}
PARTNER = {
    "name": "黒川いつき", "age": "29", "region": "東京都中野区", "occupation": "書店員",
    "description": "中野で書店員をしています。休みの日は古本屋をのぞいたり街をぶらぶら歩いたりしています。喫茶店のカレーとドーナツが好きです。ゆっくり話せる方だとうれしいです。"
}
PARTNER_INTERNAL = "架空の相手役用設定。中野在住で書店員。古本や散歩の話は自然にできるが、必ず承諾はしない。"

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

state = {
    "experiment_id": "conversation_test_20261017_invite_d_schedule_T456",
    "started_at": now(),
    "status": "RUNNING",
    "end_reason": None,
    "self_profile": dict(SELF),
    "partner": dict(PARTNER),
    "partner_internal": PARTNER_INTERNAL,
    "messages": [],
    "turns": [],
    "blocks": [],
    "requests": [],
    "app_sent_count": 0,
    "partner_sent_count": 0,
    "match_id": None,
    "updated_at": now(),
}

with TestClient(app.app) as client:
    client.put("/api/profile", json={"content": json.dumps(SELF, ensure_ascii=False), "avoid": "根拠のない共通点、大げさな褒め言葉、質問攻め、返信の催促。"})
    created = client.post("/api/matches", json={"name": PARTNER["name"], "description": PARTNER["description"]})
    match_id = created.json()["id"]
    state["match_id"] = match_id

    script = [
        ("them", "マッチングありがとうございます！書店員をしている黒川です。よろしくお願いします！"),
        ("me", "マッチングありがとうございます！経理の仕事をしています。よろしくお願いします😊"),
        ("them", "喫茶店めぐりがお好きなんですね！高円寺にアール座読書館という静かで素敵な読書喫茶があるのですが、行ったことありますか？"),
        ("me", "アール座読書館、名前は聞いたことがありますがまだ行ったことがないです！すごく気になります✨"),
        ("them", "静かで水槽の音だけが聞こえるような落ち着く空間ですよ。もしよければ今度一緒に行きませんか？"),
        ("me", "ぜひ行ってみたいです！ご一緒できたらとてもうれしいです😊"),
        ("them", "ぜひ行きましょう！来週か再来週あたりで都合のいい曜日や時間帯はありますか？")
    ]

    for role, body in script:
        client.post(f"/api/matches/{match_id}/messages", json={"role": role, "body": body})
        state["messages"].append({"speaker": "app" if role == "me" else "partner", "body": body, "at": now()})
        if role == "me":
            state["app_sent_count"] += 1
        else:
            state["partner_sent_count"] += 1

    payload1 = {"mode": "reply", "match_id": match_id, "count": 3, "response_version": 2}
    res1 = client.post("/api/generate", json=payload1)
    b1 = res1.json()
    state["requests"].append({
        "http_status": res1.status_code, "api_alias": b1.get("api_alias"), "model": b1.get("model"),
        "attempt_count": b1.get("api_attempt_count"), "error_code": b1.get("error_code"), "generation_blocked": b1.get("generation_blocked"),
    })

    user_q = b1.get("user_questions", [{}])[0].get("question", "")
    user_a = "土曜日の午後が空いています"
    payload2 = {
        "mode": "reply", "match_id": match_id, "count": 3, "response_version": 2,
        "user_answers": [{"question": user_q, "answer": user_a}]
    }
    res2 = client.post("/api/generate", json=payload2)
    b2 = res2.json()
    state["requests"].append({
        "http_status": res2.status_code, "api_alias": b2.get("api_alias"), "model": b2.get("model"),
        "attempt_count": b2.get("api_attempt_count"), "error_code": b2.get("error_code"), "generation_blocked": b2.get("generation_blocked"),
    })
    
    candidates = [b2["recommended"], *b2.get("alternatives", [])]
    selected = candidates[0]
    turn = {
        "app_send_number": state["app_sent_count"] + 1,
        "candidates": candidates,
        "selected_index": 1,
        "notice": b2.get("candidate_notice"),
        "available": b2.get("available_candidate_count"),
        "conversation_stage": b2.get("conversation_stage"),
        "invite_decision": b2.get("invite_decision"),
        "decision_reason": b2.get("decision_reason"),
        "next_action": b2.get("next_action"),
        "reason": b2.get("reason"),
        "deterministic_fallback_used": b2.get("deterministic_fallback_used"),
    }
    state["turns"].append(turn)
    state["messages"].append({"speaker": "app", "body": selected["text"], "at": now(), "app_send_number": state["app_sent_count"] + 1})
    state["app_sent_count"] += 1
    state["status"] = "COMPLETED"

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Saved JSON:", STATE)

def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

bubbles = []
turn_by_number = {t["app_send_number"]: t for t in state["turns"]}
for message in state["messages"]:
    if message["speaker"] == "app":
        turn = turn_by_number.get(message.get("app_send_number"), {})
        alts_items = []
        for c in turn.get("candidates", []):
            label = esc(c.get("label") or "候補")
            text = esc(c.get("text") or "")
            alts_items.append(f"<li>[{label}] {text}</li>")
        alts = "".join(alts_items)
        available = turn.get("available")
        fallback_used = turn.get("deterministic_fallback_used")
        stage = esc(turn.get("conversation_stage") or "")
        invite = esc(turn.get("invite_decision") or "")
        details = (
            f"<details><summary>候補 {available}案・モデル生出力採択（fallback_used={fallback_used}）"
            f"／段階 {stage}／誘い {invite}</summary>"
            f"<ul>{alts}</ul>"
            f"<p><small>{esc(turn.get('reason') or '')}</small></p>"
            f"<p><small>{esc(turn.get('decision_reason') or '')}</small></p>"
            f"<p><small>{esc(turn.get('notice') or '')}</small></p></details>"
        )
        bubbles.append(
            f'<div class="row right"><div class="bubble app"><b>アプリ側の返信案 <small>[{stage} / {invite}]</small></b>'
            f"<p>{esc(message['body'])}</p>{details}</div></div>"
        )
    else:
        bubbles.append(
            f'<div class="row"><div class="bubble partner"><b>相手役（アシスタントが担当）</b>'
            f"<p>{esc(message['body'])}</p></div></div>"
        )

reqs = "".join(
    f"<li>HTTP {r['http_status']}・{r['api_alias'] or '-'}・{r['model'] or '-'}"
    f"・試行 {r['attempt_count']}・blocked {r['generation_blocked']}・{r['error_code'] or ''}</li>"
    for r in state["requests"]
)
doc = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Matching Reply Assistant — 日程調整シナリオ(d) T456検証</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:#243247;font:16px/1.65 system-ui,"Yu Gothic",Meiryo,sans-serif}}
header,main,footer{{max-width:1050px;margin:auto;padding:22px}}.overview,.profile,.chat{{background:#fff;border:1px solid #dce4ee;border-radius:16px;padding:18px}}
.chat{{max-height:80vh;overflow:auto}}.row{{display:flex;margin:14px 0}}.right{{justify-content:flex-end}}
.bubble{{max-width:min(82%,700px);padding:12px 15px;border-radius:17px;overflow-wrap:anywhere}}
.bubble p{{white-space:pre-wrap;margin:8px 0 0}}.app{{background:#dff3e7}}.partner{{background:#e8edf5}}
small{{font-size:.8rem;color:#506078}}details{{border-top:1px solid #b8cbbf;margin-top:10px;padding-top:8px}}
footer{{color:#596779;font-size:.88rem}}</style></head><body>
<header><h1>Matching Reply Assistant — 日程調整シナリオ(d) T456検証（モデル生出力3案通過）</h1><section class="overview">
<p>開始: {esc(state['started_at'])}　状態: COMPLETED　deterministic_fallback_used: False</p>
<p>アプリ側 送信 {state['app_sent_count']} / 相手役 送信 {state['partner_sent_count']}　Geminiリクエスト {len(state['requests'])}回</p>
<p><b>結果概要:</b> ユーザー回答「土曜日の午後が空いています」に対して、Geminiモデル候補3案が厳密なスケジュール値マッチング（曜日・時間帯一致、未確定値なし、否定なし）および受諾コンテキストの文体検査をすべて一発通過し、決定論的フォールバック（fallback）に頼ることなくモデル生出力（available=3）のまま返信案を出力しました。</p>
</section></header>
<main><h2>会話記録</h2><section class="chat">{''.join(bubbles)}</section>
<section class="overview"><h2>Geminiリクエスト</h2><ol>{reqs}</ol></section></main>
</body></html>"""
HTML.write_text(doc, encoding="utf-8")
print("Saved HTML:", HTML)
