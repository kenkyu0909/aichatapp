"""Run at most eight fictional live-Gemini probes in an isolated SQLite database.

Credential values are read only by app.gemini_configurations() and never printed
or written. The endpoint has an enforced per-request provider-attempt ceiling.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
API_DIR_VALUE = os.environ.get("MRA_API_DIR", "").strip()
API_DIR = Path(API_DIR_VALUE).expanduser() if API_DIR_VALUE else None
OUTPUT = ROOT / "docs" / "verification" / "simulations" / "quality_checks_004.json"
MAX_LOGICAL_REQUESTS = 8
MAX_PROVIDER_ATTEMPTS_PER_REQUEST = 4
MAX_TOTAL_PROVIDER_ATTEMPTS = MAX_LOGICAL_REQUESTS * MAX_PROVIDER_ATTEMPTS_PER_REQUEST
PROFILE = {
    "name": "架空の水野けい",
    "age": 29,
    "region": "東京都練馬区",
    "occupation": "建築会社の事務",
    "hobbies": ["映画鑑賞", "読書", "カフェ巡り"],
    "conversation_preference": "短く自然な会話。質問は一度に一つ程度",
    "avoid": "未確認の好みや経験、共通点、予定の創作",
}
FACT_CASES = [
    {
        "id": "purchase_habit_answered",
        "question": "気になる新作を見つけたらすぐ買うタイプですか？",
        "answer": "気になった新作は少し調べてから買うことが多いです",
        "fact_markers": ["少し調べてから", "買うことが多い"],
        "description": "購買傾向の確認回答後",
    },
    {
        "id": "curry_preference_answered",
        "question": "カレーだと何が好きですか？",
        "answer": "辛さ控えめのチキンカレーが好きです",
        "fact_markers": ["辛さ控えめ", "チキンカレー"],
        "description": "カレーの具体的な好みの確認回答後",
    },
    {
        "id": "reading_genre_answered",
        "question": "普段どんなジャンルの本を読みますか？",
        "answer": "ミステリー小説を読むことが多いです",
        "fact_markers": ["ミステリー", "読むことが多い"],
        "description": "読書ジャンルの確認回答後",
    },
    {
        "id": "recent_movie_answered",
        "question": "最近どんな映画を観ましたか？",
        "answer": "最近は架空作品の『青い灯台』を観ました",
        "fact_markers": ["最近", "青い灯台", "観ました"],
        "description": "最近の視聴経験の確認回答後",
    },
]
QUALITY_CASES = [
    {
        "id": "short_mirroring_and_repetition",
        "latest": "カフェ好きです！",
        "history": [
            ("them", "休日は友達と出かけました！"),
            ("me", "いいですね！"),
            ("them", "新しいカフェも探してます笑"),
            ("me", "カフェ気になりますね！"),
        ],
        "description": "短文に合わせた文量と相槌の反復",
    },
    {
        "id": "medium_mirroring_and_tone",
        "latest": "休日は友達とカフェに行くことが多いです！最近は新しいお店も探してます笑",
        "history": [],
        "description": "複数文の明るさと軽い冗談への適応",
    },
    {
        "id": "invite_opportunity",
        "latest": "中野で落ち着いたカフェを見つけました！ケーキもおいしそうで気になってます",
        "history": [
            ("them", "休日はカフェを探すのが好きです"),
            ("me", "落ち着いたお店が好きです！"),
            ("them", "私も静かなところが好きです！けいさんはどんなお店に行きますか？"),
            ("me", "季節のタルトがあるお店を選ぶことが多いです！"),
        ],
        "description": "相互質問とカフェの話題がある誘い機会",
    },
    {
        "id": "respect_decline",
        "latest": "ごめんなさい！まだ会うのはちょっと不安です",
        "history": [
            ("them", "カフェの話楽しいですね"),
            ("me", "よかったら今度一緒に行きませんか？"),
        ],
        "description": "相手の慎重な返事を尊重する",
    },
]
SECRET_PATTERN = re.compile(r"AIza[0-9A-Za-z_-]{30,}")
REQUIRED_PROVIDER_PRIORITY = [
    ("API1", "gemini-3.5-flash-lite"),
    ("API2", "gemini-3.5-flash-lite"),
    ("API1", "gemini-3.1-flash-lite"),
    ("API2", "gemini-3.1-flash-lite"),
]


def answer_fact_is_present(candidate_text: str, fact_markers: list[str]) -> bool:
    normalized = re.sub(r"[\s『』「」。、！？!?]", "", candidate_text)
    return all(re.sub(r"[\s『』「」。、！？!?]", "", marker) in normalized for marker in fact_markers)


def provider_priority_matches(configured: list[dict[str, str]]) -> bool:
    return [(item["api_alias"], item["model"]) for item in configured] == REQUIRED_PROVIDER_PRIORITY


def save(state: dict[str, Any]) -> None:
    temp = OUTPUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(OUTPUT)


def create_match(client: TestClient, name: str, description: str, messages: list[tuple[str, str]]) -> int:
    response = client.post("/api/matches", json={"name": name, "description": description})
    if response.status_code != 201:
        raise RuntimeError("架空プロフィールを隔離SQLiteへ登録できませんでした")
    match_id = response.json()["id"]
    for role, body in messages:
        saved = client.post(f"/api/matches/{match_id}/messages", json={"role": role, "body": body})
        if saved.status_code != 201:
            raise RuntimeError("架空会話を隔離SQLiteへ登録できませんでした")
    return match_id


def summarize(body: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    if isinstance(body.get("recommended"), dict):
        candidates.append(body["recommended"])
    candidates.extend(item for item in body.get("alternatives", []) if isinstance(item, dict))
    texts = [candidate.get("text", "") for candidate in candidates]
    normalized = [re.sub(r"\s+", "", text) for text in texts]
    unsupported = []
    if candidates:
        unsupported = context["backend"].unsupported_personal_claim_topics(
            [context["backend"].Candidate(label=item.get("label", ""), text=item.get("text", "")) for item in candidates],
            context["generation_context"],
        )
    return {
        "needs_user_info": body.get("needs_user_info"),
        "generation_blocked": body.get("generation_blocked"),
        "candidates": candidates,
        "candidate_character_counts": [len(text) for text in texts],
        "candidate_sentence_estimates": [
            len([part for part in re.split(r"[!?！？]+|\n+|[ \t]+", text.strip()) if part])
            for text in texts
        ],
        "punctuation_violation": any("、" in text or "。" in text for text in texts),
        "candidate_distinct_count": len(set(normalized)),
        "unsupported_personal_claim_topics": unsupported,
        "reason": body.get("reason", ""),
        "strategy": body.get("strategy", ""),
        "conversation_stage": body.get("conversation_stage", ""),
        "invite_decision": body.get("invite_decision", ""),
        "decision_reason": body.get("decision_reason", ""),
        "next_action": body.get("next_action", ""),
        "user_questions": body.get("user_questions", []),
        "error_code": body.get("error_code"),
        "safe_error": body.get("detail"),
        "api_alias": body.get("api_alias"),
        "model": body.get("model"),
        "api_attempt_count": body.get("api_attempt_count", 0),
        "attempted_models": body.get("attempted_models", []),
    }


def main() -> int:
    global OUTPUT
    if OUTPUT.exists():
        raise SystemExit("quality_checks_004.json already exists; refusing to overwrite it")
    if API_DIR is None or not API_DIR.is_dir():
        raise SystemExit("The user-authorized private API directory is unavailable")

    os.environ["MRA_API_DIR"] = str(API_DIR)
    os.environ["MRA_MAX_PROVIDER_ATTEMPTS_PER_GENERATE"] = str(MAX_PROVIDER_ATTEMPTS_PER_REQUEST)
    os.environ["MRA_PROVIDER_MIN_INTERVAL_SECONDS"] = "4.05"
    for name in ("MRA_API_1_KEY", "MRA_API_2_KEY", "GEMINI_API_KEY"):
        os.environ.pop(name, None)
    temp_data = Path(tempfile.mkdtemp(prefix="mra-quality-004-"))
    os.environ["APP_DATA_DIR"] = str(temp_data)
    spec = importlib.util.spec_from_file_location("mra_quality_004_app", ROOT / "app.py")
    if spec is None or spec.loader is None:
        raise SystemExit("Application module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    configured = [{"api_alias": alias, "model": model} for alias, _key, model in module.gemini_configurations()]

    state: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": "quality_checks_004",
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "environment": {
            "os": "Windows",
            "python": sys.version.split()[0],
            "browser": "Firefox (separate UI regression)",
            "database": "new isolated temporary SQLite",
        },
        "credential_source": "user-authorized private API directory; values excluded",
        "configured_pairs": configured,
        "profile": PROFILE,
        "logical_request_limit": MAX_LOGICAL_REQUESTS,
        "per_request_provider_attempt_limit": MAX_PROVIDER_ATTEMPTS_PER_REQUEST,
        "total_provider_attempt_limit": MAX_TOTAL_PROVIDER_ATTEMPTS,
        "tests": [],
        "logical_requests": 0,
        "provider_attempts": 0,
        "status": "RUNNING",
        "limitations": [
            "model output is a sample and does not guarantee future quality",
            "personal-claim scanner covers known Japanese patterns and is not complete semantic verification",
            "API billing and remaining quota are not exposed by this test",
        ],
    }
    save(state)

    if not configured:
        state["status"] = "BLOCKED"
        state["blocking_reason"] = "No API configuration was available in the authorized source"
        state["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        save(state)
        print("status=BLOCKED logical_requests=0 provider_attempts=0 credentials=not_displayed")
        return 2

    if not provider_priority_matches(configured):
        state["status"] = "FAIL"
        state["blocking_reason"] = "Configured API alias/model sequence does not match required priority"
        save(state)
        print("status=FAIL logical_requests=0 provider_attempts=0 credentials=not_displayed")
        return 2

    next_allowed_at = 0.0
    blocked_codes = {"all_models_rate_limited", "api_permission_denied", "model_unavailable", "gemini_connection_error", "request_attempt_limit"}
    with TestClient(module.app) as client:
        client.put("/api/profile", json={"content": json.dumps(PROFILE, ensure_ascii=False), "avoid": PROFILE["avoid"]})
        fact_cases: list[dict[str, Any]] = []

        # Four deterministic local preflights should ask the user before any provider call.
        for index, case in enumerate(FACT_CASES):
            match_id = create_match(client, f"架空の相手{index + 1}", "映画やカレーや読書の話が好きです", [("them", case["question"])])
            preflight = client.post("/api/generate", json={
                "mode": "reply", "match_id": match_id, "response_version": 2,
            }).json()
            preflight_ok = bool(preflight.get("needs_user_info")) and not preflight.get("recommended") and not preflight.get("alternatives") and preflight.get("api_attempt_count", 0) == 0
            preflight_record = {
                "phase": "local_preflight",
                "result": "PASS" if preflight_ok else "FAIL",
                "input_question": case["question"],
                "user_questions": preflight.get("user_questions", []),
                "api_attempt_count": preflight.get("api_attempt_count", 0),
            }
            state["tests"].append({"id": f"{case['id']}_preflight", **preflight_record})
            save(state)
            if not preflight_ok:
                state["status"] = "FAIL"
                state["blocking_reason"] = "A local direct-question preflight returned an unsafe result"
                break
            fact_cases.append({**case, "match_id": match_id, "user_question": preflight["user_questions"][0]["question"]})

        if state["status"] == "RUNNING":
            requests: list[dict[str, Any]] = []
            for case in fact_cases:
                requests.append({
                    "id": case["id"],
                    "description": case["description"],
                    "mode": "reply",
                    "match_id": case["match_id"],
                    "user_answers": [{"question": case["user_question"], "answer": case["answer"]}],
                    "expected_answer": case["answer"],
                })
            for case in QUALITY_CASES:
                history = case["history"] + [("them", case["latest"])]
                match_id = create_match(client, f"架空_{case['id']}", "カフェや映画が好きな架空プロフィールです", history)
                requests.append({
                    "id": case["id"], "description": case["description"], "mode": "reply",
                    "match_id": match_id, "user_answers": [], "expected_answer": None,
                })

            for request in requests[:MAX_LOGICAL_REQUESTS]:
                if state["logical_requests"] >= MAX_LOGICAL_REQUESTS:
                    state["status"] = "BLOCKED"
                    state["blocking_reason"] = "Logical request ceiling reached before another request"
                    break
                if state["provider_attempts"] + MAX_PROVIDER_ATTEMPTS_PER_REQUEST > MAX_TOTAL_PROVIDER_ATTEMPTS:
                    state["status"] = "BLOCKED"
                    state["blocking_reason"] = "Provider attempt ceiling would be exceeded"
                    break
                generation_context = module.build_context(module.GenerateInput(
                    mode="reply", match_id=request["match_id"], response_version=2,
                    user_answers=request["user_answers"],
                ))
                wait_for = next_allowed_at - time.monotonic()
                if wait_for > 0:
                    time.sleep(wait_for)
                state["logical_requests"] += 1
                response = client.post("/api/generate", json={
                    "mode": request["mode"], "match_id": request["match_id"],
                    "response_version": 2, "count": 3,
                    "user_answers": request["user_answers"],
                })
                body = response.json()
                result = summarize(body, {"backend": module, "generation_context": generation_context})
                state["provider_attempts"] += result["api_attempt_count"]
                attempted = result["attempted_models"]
                if attempted:
                    next_allowed_at = time.monotonic() + 4.05
                candidate_text = "\n".join(item.get("text", "") for item in result["candidates"])
                contains_secret_pattern = bool(SECRET_PATTERN.search(candidate_text))
                if contains_secret_pattern:
                    result["candidates"] = [{"label": "redacted", "text": "[出力に認証情報らしい文字列が検出されたため非表示]"}]
                    result["secret_like_output_redacted"] = True
                needs_answer = request["id"].endswith("_answered")
                content_ok = (
                    response.status_code == 200
                    and result["needs_user_info"] is False
                    and len(result["candidates"]) == 3
                    and not result["punctuation_violation"]
                    and result["candidate_distinct_count"] == 3
                    and not result["unsupported_personal_claim_topics"]
                    and (not needs_answer or answer_fact_is_present(
                        candidate_text, next(case["fact_markers"] for case in FACT_CASES if case["id"] == request["id"])
                    ))
                    and not contains_secret_pattern
                )
                if request["id"] == "invite_opportunity":
                    has_invitation = any(
                        re.search(r"(?:一緒に|今度|よかったら).{0,24}(?:行きません|行けたら|どうですか)", item.get("text", ""))
                        for item in result["candidates"]
                    )
                    context_ready = module.invite_opportunity_ready(generation_context)
                    content_ok = content_ok and not (
                        result["invite_decision"] == "consider_invite" and context_ready and not has_invitation
                    )
                    content_ok = content_ok and not (result["invite_decision"] == "invite_gently" and not has_invitation)
                if request["id"] == "respect_decline":
                    content_ok = content_ok and result["invite_decision"] in {"respect_no", "do_not_repeat_invite", "wait", "continue_or_close"} and not any(
                        re.search(r"(?:一緒に|今度|よかったら).{0,24}(?:行きません|行けたら|どうですか)", item.get("text", ""))
                        for item in result["candidates"]
                    )
                result["http_status"] = response.status_code
                result["result"] = "PASS" if content_ok else "FAIL"
                if contains_secret_pattern:
                    result["result"] = "BLOCKED"
                test_record = {
                    "id": request["id"],
                    "description": request["description"],
                    "input": {
                        "partner_latest_message": next((message["body"] for message in reversed(generation_context["history"]) if message["role"] == "them"), ""),
                        "user_answer": request["user_answers"],
                        "fictional_profile": PROFILE,
                    },
                    "evaluation": result,
                }
                state["tests"].append(test_record)
                save(state)
                if result.get("error_code") in blocked_codes or contains_secret_pattern:
                    state["status"] = "BLOCKED"
                    state["blocking_reason"] = "Stopped after an API, attempt-limit, or output-safety error"
                    break
                if not content_ok:
                    state["status"] = "FAIL"

    if state["status"] == "RUNNING":
        state["status"] = "PASS" if all(
            item.get("result") == "PASS" for item in state["tests"] if item.get("phase") != "local_preflight"
        ) else "FAIL"
    state["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save(state)
    print(
        f"status={state['status']} logical_requests={state['logical_requests']} "
        f"provider_attempts={state['provider_attempts']} credential_values=not_displayed output={OUTPUT.name}"
    )
    return 0 if state["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
