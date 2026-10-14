"""Run fictional live-Gemini quality probes against an isolated temporary SQLite DB.

API credentials are read only by app.gemini_configurations() from the user's private
API directory. This script never prints or serializes credential values.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
API_DIR = Path(r"C:\Users\poiuy\Desktop\aichatapp2\API")
OUTPUT = ROOT / "docs" / "verification" / "simulations" / "quality_checks_003.json"
MAX_PROVIDER_ATTEMPTS = 25
MAX_ATTEMPTS_PER_LOGICAL_REQUEST = 5
PROFILE = {
    "name": "架空の橘はる",
    "age": 28,
    "region": "東京都杉並区",
    "occupation": "建築事務所の事務",
    "hobbies": ["喫茶店めぐり", "植物の世話", "小さな美術館"],
    "food": ["オムライス", "季節のタルト"],
    "weekends": "喫茶店に行ったり植物の手入れをしたりする",
    "conversation_preference": "短く自然な会話。質問は一度に一つ程度",
    "avoid": "未確認の共通点、過度な褒め言葉、質問攻め、予定の断定。",
}
CASES = [
    ("A_short", "カフェ好きです！", []),
    ("B_two_or_three_sentences", "休日は友達とカフェに行くことが多いです！最近は新しいお店も探してます笑", []),
    ("C_calm", "昨日は家で映画を観ていました", []),
    ("D_joke", "休みの日ほとんど寝てました笑", []),
    ("E_serious", "最近仕事が忙しくて疲れています", []),
    ("F_repeated_topic", "映画館の音響って迫力ありますよね！", [
        ("them", "映画館の大きなスクリーンが好きです"),
        ("me", "大きなスクリーンは迫力がありますよね！"),
        ("them", "音響もすごくいいですよね！"),
        ("me", "音響の迫力も映画館の魅力ですよね！"),
    ]),
    ("G_invite_opportunity", "中野に落ち着いたカフェを見つけました！行ってみたいです", [
        ("them", "喫茶店を探すのが好きなんです"),
        ("me", "どんな雰囲気のお店が好きですか？"),
        ("them", "静かでケーキがおいしいところが好きです！はるさんはどんなお店が好きですか？"),
        ("me", "喫茶店で季節のタルトを食べるのが好きです！"),
    ]),
    ("H_decline", "ごめんなさい！まだ会うのはちょっと不安です", [
        ("them", "カフェの話楽しいですね"),
        ("me", "よかったら今度一緒に行きませんか？"),
    ]),
]


def atomic_save(value: dict[str, Any]) -> None:
    temp = OUTPUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(OUTPUT)


def messages_for(c: TestClient, match_id: int, messages: list[tuple[str, str]]) -> None:
    role_map = {"me": "me", "them": "them"}
    for role, body in messages:
        response = c.post(f"/api/matches/{match_id}/messages", json={"role": role_map[role], "body": body})
        if response.status_code != 201:
            raise RuntimeError("架空の会話履歴を一時SQLiteへ保存できませんでした")


def summarize_response(response: Any) -> dict[str, Any]:
    data = response.json()
    candidates = []
    if isinstance(data.get("recommended"), dict):
        candidates.append(data["recommended"])
    candidates.extend(item for item in data.get("alternatives", []) if isinstance(item, dict))
    normalized = ["".join((c.get("text") or "").split()) for c in candidates]
    return {
        "http_status": response.status_code,
        "needs_user_info": data.get("needs_user_info"),
        "generation_blocked": data.get("generation_blocked"),
        "demo": data.get("demo"),
        "api_alias": data.get("api_alias"),
        "model": data.get("model"),
        "api_attempt_count": data.get("api_attempt_count", 0),
        "attempted_models": data.get("attempted_models", []),
        "error_code": data.get("error_code"),
        "safe_error": data.get("detail"),
        "user_questions": data.get("user_questions", []),
        "candidates": candidates,
        "candidate_character_counts": [len(c.get("text", "")) for c in candidates],
        "candidate_sentence_estimates": [max(1, sum(1 for ch in c.get("text", "") if ch in "!?！？\n")) for c in candidates],
        "punctuation_violation": any("、" in c.get("text", "") or "。" in c.get("text", "") for c in candidates),
        "candidate_distinct_count": len(set(normalized)),
        "strategy": data.get("strategy"),
        "conversation_stage": data.get("conversation_stage"),
        "invite_decision": data.get("invite_decision"),
        "decision_reason": data.get("decision_reason"),
        "next_action": data.get("next_action"),
    }


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit("quality_checks_003.json already exists; refusing to overwrite it")
    if not API_DIR.is_dir():
        raise SystemExit("The user-provided private API directory is unavailable")
    os.environ["MRA_API_DIR"] = str(API_DIR)
    os.environ["MRA_PROVIDER_MIN_INTERVAL_SECONDS"] = "4.05"
    for name in ("MRA_API_1_KEY", "MRA_API_2_KEY", "GEMINI_API_KEY"):
        os.environ.pop(name, None)
    temp_data = Path(tempfile.mkdtemp(prefix="mra-quality-003-"))
    os.environ["APP_DATA_DIR"] = str(temp_data)
    spec = importlib.util.spec_from_file_location("mra_quality_check_app", ROOT / "app.py")
    app_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = app_module
    spec.loader.exec_module(app_module)
    configurations = app_module.gemini_configurations()
    configured = [{"api_alias": alias, "model": model} for alias, _key, model in configurations]
    state: dict[str, Any] = {
        "schema_version": 1,
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "environment": {"os": "Windows", "python": sys.version.split()[0], "browser": "Firefox (separate UI verification)", "database": "isolated temporary SQLite"},
        "credential_source": "user-authorized API directory; credential values excluded",
        "configured_pairs": configured,
        "profile": PROFILE,
        "tests": [],
        "logical_requests": 0,
        "provider_attempts": 0,
        "provider_attempts_unknown": 0,
        "status": "RUNNING",
        "limitations": ["quality ratings require human review", "profile-claim guard uses conservative patterns and is not a complete semantic fact checker"],
    }
    atomic_save(state)

    with TestClient(app_module.app) as client:
        client.put("/api/profile", json={"content": json.dumps(PROFILE, ensure_ascii=False), "avoid": PROFILE["avoid"]})

        # T77: prove preflight asks locally before any Gemini call, then test one live answer.
        created = client.post("/api/matches", json={"name": "架空のりお", "description": "休日は美術館やカフェに行きます"})
        match_id = created.json()["id"]
        client.post(f"/api/matches/{match_id}/messages", json={"role": "them", "body": "映画好きですか？"})
        preflight = client.post("/api/generate", json={"mode": "reply", "match_id": match_id, "response_version": 2})
        preflight_summary = summarize_response(preflight)
        preflight_test = {
            "id": "T77_preflight",
            "input": {"partner_message": "映画好きですか？", "profile_has_movie_fact": False},
            "expected": "asks user and returns no recipient candidate before any Gemini call",
            "result": preflight_summary,
            "evaluation": "PASS" if preflight_summary["needs_user_info"] and not preflight_summary["candidates"] and preflight_summary["api_attempt_count"] == 0 else "FAIL",
            "method": "local application preflight; no external API request",
        }
        state["tests"].append(preflight_test)
        atomic_save(state)

        answer_payload = {
            "mode": "reply", "match_id": match_id, "response_version": 2,
            "user_answers": [{"question": "映画はお好きですか？", "answer": "映画好きです！特に洋画をよく観ます"}],
        }
        next_allowed_at = 0.0
        cases = [("T77_answered", "映画好きですか？", [])] + CASES
        for case_id, latest, history in cases:
            # Reserve the backend's worst-case attempts before starting another
            # logical request so the overall provider-attempt cap cannot be crossed.
            if state["provider_attempts"] + MAX_ATTEMPTS_PER_LOGICAL_REQUEST > MAX_PROVIDER_ATTEMPTS:
                state["status"] = "BLOCKED"
                state["blocking_reason"] = "Stopped before starting a request that could exceed the provider-attempt budget"
                break
            if case_id != "T77_answered":
                created = client.post("/api/matches", json={"name": f"架空_{case_id}", "description": "カフェや散歩が好きな架空人物です"})
                match_id = created.json()["id"]
                messages_for(client, match_id, history + [("them", latest)])
                request = {"mode": "reply", "match_id": match_id, "response_version": 2}
            else:
                request = answer_payload

            wait_for = next_allowed_at - time.monotonic()
            if wait_for > 0:
                time.sleep(wait_for)
            state["logical_requests"] += 1
            try:
                response = client.post("/api/generate", json=request)
                summary = summarize_response(response)
            except Exception as exc:
                summary = {"transport_error_type": type(exc).__name__, "provider_attempt_count_unknown": True}
                state["status"] = "BLOCKED"
                state["blocking_reason"] = "Gemini transport/API call failed; internal exception text was not recorded"
                state["provider_attempts_unknown"] += 1
                state["last_attempt_count_status"] = "unknown: request may have reached the provider before transport failure"
            next_allowed_at = time.monotonic() + 4.2
            attempts = summary.get("api_attempt_count", 0)
            state["provider_attempts"] += attempts
            text_out = " ".join(c.get("text", "") for c in summary.get("candidates", []))
            substantive_result = (
                summary.get("http_status") == 200
                and summary.get("demo") is False
                and len(summary.get("candidates", [])) == 3
                and summary.get("punctuation_violation") is False
                and summary.get("candidate_distinct_count") == 3
            )
            test_result = {
                "id": case_id,
                "input": {
                    "partner_message": latest,
                    "prior_messages": history,
                    "profile_has_topic_fact": False,
                    "temporary_user_answer_supplied": case_id == "T77_answered",
                    "temporary_user_answer": "映画好きです！特に洋画をよく観ます" if case_id == "T77_answered" else None,
                },
                "expected": "three distinct live candidates when generation is safe; no Japanese comma/period in recipient text",
                "result": summary,
                "method": "real Gemini through existing /api/generate; fictional profile and isolated SQLite",
                "evaluation": "PASS" if substantive_result else ("BLOCKED" if summary.get("http_status", 200) != 200 or state["status"] == "BLOCKED" else "FAIL"),
                "human_quality_review": "PENDING",
                "heuristic_assessment": {
                    "nonempty_candidate_text": bool(text_out),
                    "all_candidates_distinct": summary.get("candidate_distinct_count") == 3,
                    "candidate_style_review_required": True,
                },
            }
            state["tests"].append(test_result)
            atomic_save(state)
            print(f"{case_id}: HTTP {summary.get('http_status', 'transport-error')} alias={summary.get('api_alias')} model={summary.get('model')} attempts={attempts} candidates={len(summary.get('candidates', []))}")
            if state["status"] == "BLOCKED" or summary.get("http_status") != 200:
                state["status"] = "BLOCKED"
                state["blocking_reason"] = summary.get("safe_error") or "API request did not complete successfully"
                break
            if summary.get("error_code") in ("all_models_rate_limited", "api_permission_denied", "model_not_found"):
                state["status"] = "BLOCKED"
                state["blocking_reason"] = summary.get("safe_error") or summary["error_code"]
                break
        else:
            state["status"] = "COMPLETED"
    state["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    atomic_save(state)
    print(f"saved={OUTPUT.relative_to(ROOT)} status={state['status']} logical_requests={state['logical_requests']} provider_attempts={state['provider_attempts']}")
    return 0 if state["status"] == "COMPLETED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
