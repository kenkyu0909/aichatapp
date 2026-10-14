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
OUTPUT = ROOT / "docs" / "verification" / "simulations" / "quality_checks_006.json"
MAX_LOGICAL_REQUESTS = 8
MAX_PROVIDER_ATTEMPTS_PER_REQUEST = 4
MAX_TOTAL_PROVIDER_ATTEMPTS = MAX_LOGICAL_REQUESTS * MAX_PROVIDER_ATTEMPTS_PER_REQUEST
PROFILE = {
    "name": "架空の水野けい",
    "age": 29,
    "region": "東京都練馬区",
    "occupation": "建築会社の事務",
    "hobbies": ["読書", "カフェ巡り"],
    "conversation_preference": "短く自然な会話。質問は一度に一つ程度",
    "avoid": "未確認の好みや経験、共通点、予定の創作",
}
FACT_CASES = [
    {
        "id": "reading_genre_answered",
        "question": "普段どんなジャンルの本を読みますか？",
        "expected_question_markers": ["ジャンル", "本"],
        "answer": "ミステリー小説を読むことが多いです",
        "fact_markers": ["ミステリー", "読むことが多い"],
        "description": "読書ジャンルの確認回答後",
    },
    {
        "id": "recent_movie_answered",
        "question": "最近どんな映画を観ましたか？",
        "expected_question_markers": ["最近", "映画"],
        "answer": "最近は架空作品の『青い灯台』を観ました",
        "fact_markers": ["最近", "青い灯台", "観ました"],
        "description": "最近の視聴経験の確認回答後",
    },
]
QUALITY_CASES = [
    {
        "id": "purchase_habit_answered",
        "latest": "気になる新作を見つけたらすぐ買うタイプですか？",
        "history": [],
        "user_answers": [{"question": "気になる新作を見つけたらすぐ買うタイプですか？", "answer": "気になった新作は少し調べてから買うことが多いです"}],
        "expected_answer": "気になった新作は少し調べてから買うことが多いです",
        "fact_markers": ["少し調べてから", "買うことが多い"],
        "description": "確認済みの買い方と矛盾しない返信",
    },
    {
        "id": "respect_decline_and_no_reask",
        "latest": "ごめんなさい！まだ会うのはちょっと不安です",
        "history": [
            ("them", "休日は友達とカフェに行くことが多いです！"),
            ("me", "よかったら今度カフェに行きませんか？"),
        ],
        "user_answers": [], "expected_answer": None,
        "description": "誘いへの慎重な反応を尊重し既知のカフェ頻度を再質問しない",
    },
    {
        "id": "placeholder_free",
        "latest": "本の話をしていると楽しいですね！",
        "history": [],
        "user_answers": [], "expected_answer": None,
        "description": "候補に名前などの未完成プレースホルダーを含めない",
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
        "user_answers": [], "expected_answer": None,
        "description": "相互質問とカフェの話題がある誘い機会",
    },
    {
        "id": "newline_per_sentence",
        "latest": "休日は友達とカフェに行くことが多いです！最近は新しいお店も探してます笑",
        "history": [], "user_answers": [], "expected_answer": None,
        "description": "各候補を1文ごとに改行し短文相手への分量を合わせる",
    },
    {
        "id": "empathy_variety",
        "latest": "映画館の大きなスクリーンって迫力がありますよね！",
        "history": [
            ("them", "映画館の音響っていいですよね"),
            ("me", "映画館の音響いいですよね！"),
            ("them", "大きなスクリーンも好きです"),
            ("me", "大きなスクリーンいいですよね！"),
        ],
        "user_answers": [], "expected_answer": None,
        "description": "同じ共感の言い換えを続けず話題を前へ進める",
    },
]
SECRET_PATTERN = re.compile(r"AIza[0-9A-Za-z_-]{30,}")
REQUIRED_PROVIDER_PRIORITY = [
    ("API1", "gemini-3.5-flash-lite"),
    ("API2", "gemini-3.5-flash-lite"),
    ("API1", "gemini-3.1-flash-lite"),
    ("API2", "gemini-3.1-flash-lite"),
]
INVITATION_PATTERN = re.compile(
    r"(?:"
    r"(?:今度|よかったら|もしよければ|一緒に|ご一緒).{0,32}(?:会いませんか|会えたら|行きませんか|行きましょう|しませんか|どうですか)"
    r"|(?:会いませんか|会えたら|行きませんか|行きましょう)"
    r"|(?:ご飯|食事|カフェ|お茶)(?:で|に|でも|へ|を食べに|食べに|に行って|行って).{0,16}(?:どうですか|しませんか|行きませんか|行きましょう)"
    r")"
)


def decline_and_no_reask_is_safe(result: dict[str, Any]) -> bool:
    """Require a respectful decision, no new invitation, and no repeated known fact."""
    candidates = result.get("candidates", [])
    return (
        result.get("invite_decision") in {"respect_no", "do_not_repeat_invite", "wait", "continue_or_close", "do_not_invite"}
        and not any(INVITATION_PATTERN.search(item.get("text", "")) for item in candidates)
        and "友達とカフェに行く頻度" not in result.get("repeated_partner_fact_topics", [])
    )


def answer_fact_is_present(candidate_text: str, fact_markers: list[str]) -> bool:
    normalized = re.sub(r"[\s『』「」。、！？!?]", "", candidate_text)
    return all(re.sub(r"[\s『』「」。、！？!?]", "", marker) in normalized for marker in fact_markers)


def at_least_one_candidate_uses_answer_facts(candidates: list[dict[str, Any]], fact_markers: list[str]) -> bool:
    """Ensure the answer can be used without requiring every safe option to repeat it."""
    return bool(candidates) and any(
        answer_fact_is_present(item.get("text", ""), fact_markers)
        for item in candidates
    )


def provider_priority_matches(configured: list[dict[str, str]]) -> bool:
    return [(item["api_alias"], item["model"]) for item in configured] == REQUIRED_PROVIDER_PRIORITY


def save(state: dict[str, Any]) -> None:
    temp = OUTPUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(OUTPUT)


def select_authorized_api_source(api_dir: Path) -> None:
    """Force the runner to use the explicitly authorized private API files only."""
    os.environ["MRA_API_DIR"] = str(api_dir.resolve())
    # app.py calls load_dotenv at import time. Keep blank env values present so
    # dotenv's default non-overriding behavior cannot substitute repository .env keys.
    for name in ("MRA_API_1_KEY", "MRA_API_2_KEY", "GEMINI_API_KEY"):
        os.environ[name] = ""


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
    mirroring = context["generation_context"].get("mirroring", {})
    recent_ack_counts = mirroring.get("recent_self_acknowledgment_counts", {}) if isinstance(mirroring, dict) else {}
    repeated_acknowledgment_candidates = []
    acknowledgment_patterns = {
        "共感": re.compile(r"わかります|分かります|たしかに|確かに|ですよね"),
        "納得": re.compile(r"そうなんですね|なるほど|そういうことなんですね"),
        "前向き": re.compile(r"いいですね|素敵ですね|楽しそうですね"),
        "興味": re.compile(r"気になりますね|面白そうですね|聞いてみたいです"),
    }
    for family, pattern in acknowledgment_patterns.items():
        if isinstance(recent_ack_counts, dict) and recent_ack_counts.get(family, 0) >= 2 and any(pattern.search(text) for text in texts):
            repeated_acknowledgment_candidates.append(family)
    return {
        "needs_user_info": body.get("needs_user_info"),
        "generation_blocked": body.get("generation_blocked"),
        "candidates": candidates,
        "candidate_character_counts": [len(text) for text in texts],
        "candidate_sentence_estimates": [
            len([part for part in re.split(r"[!?！？]+|\n+|[ \t]+", text.strip()) if part])
            for text in texts
        ],
        "candidate_line_counts": [len([line for line in text.splitlines() if line.strip()]) for text in texts],
        "recent_self_acknowledgment_counts": recent_ack_counts,
        "repeated_acknowledgment_candidates": repeated_acknowledgment_candidates,
        "punctuation_violation": any("、" in text or "。" in text for text in texts),
        "missing_sentence_break_violation": any(context["backend"].candidate_has_missing_sentence_break(text) for text in texts),
        "placeholder_violation": any(context["backend"].candidate_has_placeholder(text) for text in texts),
        "repeated_partner_fact_topics": context["backend"].repeated_partner_question_topics(
            [context["backend"].Candidate(label=item.get("label", ""), text=item.get("text", "")) for item in candidates],
            context["generation_context"],
        ) if candidates else [],
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
        raise SystemExit("quality_checks_006.json already exists; refusing to overwrite it")
    if API_DIR is None or not API_DIR.is_dir():
        raise SystemExit("The user-authorized private API directory is unavailable")

    select_authorized_api_source(API_DIR)
    os.environ["MRA_MAX_PROVIDER_ATTEMPTS_PER_GENERATE"] = str(MAX_PROVIDER_ATTEMPTS_PER_REQUEST)
    os.environ["MRA_PROVIDER_MIN_INTERVAL_SECONDS"] = "4.05"
    temp_data = Path(tempfile.mkdtemp(prefix="mra-quality-006-"))
    os.environ["APP_DATA_DIR"] = str(temp_data)
    spec = importlib.util.spec_from_file_location("mra_quality_006_app", ROOT / "app.py")
    if spec is None or spec.loader is None:
        raise SystemExit("Application module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    configured = [{"api_alias": alias, "model": model} for alias, _key, model in module.gemini_configurations()]

    state: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": "quality_checks_006",
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
            questions = preflight.get("user_questions", [])
            question_text = questions[0].get("question", "") if questions and isinstance(questions[0], dict) else ""
            preflight_ok = (
                bool(preflight.get("needs_user_info"))
                and not preflight.get("recommended")
                and not preflight.get("alternatives")
                and preflight.get("api_attempt_count", 0) == 0
                and all(marker in question_text for marker in case["expected_question_markers"])
            )
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
                    "fact_markers": case["fact_markers"],
                })
            for case in QUALITY_CASES:
                history = case["history"] + [("them", case["latest"])]
                match_id = create_match(client, f"架空_{case['id']}", "カフェや映画が好きな架空プロフィールです", history)
                requests.append({
                    "id": case["id"], "description": case["description"], "mode": "reply",
                    "match_id": match_id, "user_answers": case.get("user_answers", []),
                    "expected_answer": case.get("expected_answer"), "fact_markers": case.get("fact_markers", []),
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
                    and not result["missing_sentence_break_violation"]
                    and not result["placeholder_violation"]
                    and not result["repeated_partner_fact_topics"]
                    and not result["unsupported_personal_claim_topics"]
                    and (not needs_answer or at_least_one_candidate_uses_answer_facts(
                        result["candidates"], request["fact_markers"]
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
                if request["id"] == "respect_decline_and_no_reask":
                    content_ok = content_ok and decline_and_no_reask_is_safe(result)
                if request["id"] == "empathy_variety":
                    content_ok = content_ok and not result["repeated_acknowledgment_candidates"]
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
                if result.get("error_code") in blocked_codes or result.get("error_code") == "invalid_response" or contains_secret_pattern:
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
