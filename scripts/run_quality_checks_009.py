"""Bounded live Gemini quality checks using isolated fictional data.

The existing application endpoint performs all provider selection and generation.
Secret values are never emitted or persisted.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

try:
    from scripts.quality_eval import combine_quality_verdict, independent_quality_verdict
except ImportError:  # pragma: no cover - direct script execution puts scripts/ on sys.path
    from quality_eval import combine_quality_verdict, independent_quality_verdict

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(
    os.environ.get("MRA_QUALITY_OUTPUT")
    or (ROOT / "docs/verification/simulations/quality_checks_009.json")
).expanduser()
API_DIR = Path(os.environ.get("MRA_API_DIR") or (ROOT.parent / "API")).expanduser()
MAX_LOGICAL = 12
MAX_PROVIDER = 24
SMOKE_SCOPE = "Live provider response and baseline safety/content checks; excludes semantic diversity."
PROFILE = {
    "name": "架空の水野けい", "age": 29, "region": "東京都練馬区",
    "occupation": "建築会社の事務", "hobbies": ["読書", "カフェ巡り"],
    "conversation_preference": "短く自然な会話。質問は一度に一つ程度",
    "avoid": "未確認の好みや経験、共通点、予定の創作",
}
SECRET_RE = re.compile(r"AIza[0-9A-Za-z_-]{30,}")
CASES = [
    {"id": "smoke_reply", "latest": "休日は友達とカフェに行ってきました！", "history": [], "answers": []},
    {"id": "short_mirroring", "latest": "カフェ好きです！", "history": [], "answers": []},
    {"id": "joke_mirroring", "latest": "休日ほぼ寝て終わりました笑", "history": [], "answers": []},
    {"id": "direct_question_unconfirmed", "latest": "映画好きですか？", "history": [], "answers": []},
    {"id": "recent_movie_answered", "latest": "最近どんな映画を観ましたか？", "history": [], "answers": [{"question": "最近観た映画の作品名を教えてください", "answer": "最近は『青い灯台』を観ました"}]},
    {"id": "answered_purchase_fact", "latest": "気になる新作を見つけたらすぐ買うタイプですか？", "history": [], "answers": [{"question": "気になる新作を見つけたらすぐ買うタイプですか？", "answer": "気になった新作は少し調べてから買うことが多いです"}]},
    {"id": "known_partner_fact_after_fix", "latest": "最近は新しいカフェも探してます！", "history": [("them", "休日は友達とカフェに行くことが多いです！"), ("me", "いいですね！")], "answers": []},
    {"id": "invite_opportunity", "latest": "中野で落ち着いたカフェを見つけました！ケーキもおいしそうで気になってます", "history": [("them", "休日はカフェを探すのが好きです"), ("me", "落ち着いたお店が好きです！"), ("them", "私も静かなところが好きです！けいさんはどんなお店に行きますか？"), ("me", "季節のタルトがあるお店を選ぶことが多いです！")], "answers": []},
    {"id": "respect_decline_after_fix", "latest": "ごめんなさい！まだ会うのはちょっと不安です", "history": [("them", "カフェ好きです"), ("me", "よかったら今度行きませんか？")], "answers": []},
]


def smoke_candidate_set_status(
    response: dict[str, Any], actual_count: int, requested_count: int
) -> str:
    """Separate a live safe shortage from a complete smoke candidate set."""
    if response.get("demo") is not False or response.get("needs_user_info") is not False:
        return "not_applicable"
    if actual_count == requested_count:
        return "complete"
    if 0 < actual_count < requested_count:
        return "partial_safe"
    return "invalid"


def smoke_has_live_valid_response(
    response: dict[str, Any], actual_count: int, requested_count: int, provider_attempts: int
) -> bool:
    """Require evidence of a real model call while allowing safe shortages."""
    return (
        response.get("demo") is False
        and response.get("needs_user_info") is False
        and provider_attempts > 0
        and bool(response.get("model"))
        and smoke_candidate_set_status(response, actual_count, requested_count)
        in {"complete", "partial_safe"}
    )


def record_candidates(
    candidates: list[dict[str, Any]], texts: list[str], *, redacted: bool
) -> list[dict[str, Any]]:
    """Persist reply strategy metadata without retaining redacted text."""
    if redacted:
        return []
    return [
        {
            "label": candidate.get("label"),
            "reply_move": candidate.get("reply_move"),
            "text": text,
        }
        for candidate, text in zip(candidates, texts)
    ]


def candidate_set_has_semantic_redundancy(
    candidates: list[dict[str, Any]], backend_module: Any
) -> bool:
    """Use the application's semantic-redundancy gate in the quality verdict."""
    if len(candidates) < 2:
        return False
    parsed = [
        backend_module.Candidate.model_validate(candidate)
        for candidate in candidates
    ]
    return bool(backend_module._candidate_set_needs_diversity_repair(parsed))


def quality_case_result(
    content_pass: bool,
    diversity_violation: bool,
    http_status: int,
    error_code: str | None,
) -> str:
    """A safe response can still fail the separate quality-diversity check."""
    if content_pass:
        return "FAIL" if diversity_violation else "PASS"
    if http_status >= 500 or error_code:
        return "BLOCKED"
    return "FAIL"


def smoke_only_status(state: dict[str, Any]) -> str:
    """Report the quality verdict of smoke-only runs without conflating it with connectivity."""
    if state.get("smoke") != "PASS":
        return "BLOCKED" if state.get("blocking_reason") else "FAIL"
    smoke_evaluation = next(
        (
            item.get("evaluation", {})
            for item in state.get("tests", [])
            if item.get("id") == "smoke_reply"
        ),
        {},
    )
    result = smoke_evaluation.get("result")
    if result == "PASS":
        return "SMOKE_PASS"
    if result in {"FAIL", "BLOCKED"}:
        return result
    return "FAIL"


def finalize_smoke_only_state(state: dict[str, Any]) -> None:
    """Persist the distinction between live-safe smoke and the overall quality verdict."""
    state["smoke_scope"] = SMOKE_SCOPE
    state["status"] = smoke_only_status(state)


def quality_run_exit_code(status: str) -> int:
    """Treat a fully evaluated smoke-only pass as successful process completion."""
    return 0 if status in {"PASS", "SMOKE_PASS"} else 2


def save(state: dict[str, Any]) -> None:
    tmp = OUTPUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUTPUT)


def main() -> int:
    continuing = "--continue-existing" in sys.argv
    extend_existing = "--extend" in sys.argv
    retry_smoke_once = "--retry-smoke-once" in sys.argv
    retry_case_arg = next((arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--retry-case=")), "")
    if OUTPUT.exists() and not continuing:
        raise SystemExit(f"Refusing to overwrite existing {OUTPUT.name}")
    if continuing and not OUTPUT.exists():
        raise SystemExit("No existing run to continue")
    if not API_DIR.is_dir():
        raise SystemExit("Authorized API directory unavailable; secret values were not read by this runner")
    os.environ["MRA_API_DIR"] = str(API_DIR.resolve())
    for key_name in ("MRA_API_1_KEY", "MRA_API_2_KEY", "GEMINI_API_KEY"):
        os.environ[key_name] = ""
    os.environ["MRA_PROVIDER_MIN_INTERVAL_SECONDS"] = "4.05"
    temp_data = Path(tempfile.mkdtemp(prefix="mra-quality-008-"))
    os.environ["APP_DATA_DIR"] = str(temp_data)
    spec = importlib.util.spec_from_file_location("mra_quality_009_app", ROOT / "app.py")
    if spec is None or spec.loader is None:
        raise SystemExit("Application module could not be loaded")
    app_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = app_module
    spec.loader.exec_module(app_module)
    configs = app_module.gemini_configurations()
    configured = [{"api_alias": alias, "model": model} for alias, _secret, model in configs]
    if continuing:
        state = json.loads(OUTPUT.read_text(encoding="utf-8"))
        state.setdefault("smoke_scope", SMOKE_SCOPE)
        retryable_connection = (
            retry_smoke_once
            and state.get("status") == "BLOCKED"
            and state.get("blocking_reason") == "Initial smoke request unsuccessful: gemini_connection_error"
            and any(test.get("id") == "smoke_reply" for test in state.get("tests", []))
        )
        retry_target = next((case for case in CASES if case["id"] == retry_case_arg), None)
        retry_target_allowed = bool(
            retry_target
            and state.get("status") == "FAIL"
            and any(
                test.get("id") == retry_case_arg
                and test.get("evaluation", {}).get("result") == "FAIL"
                for test in state.get("tests", [])
            )
        )
        if state.get("experiment_id") != "quality_checks_009" or (
            state.get("status") not in {"SMOKE_PASS", "FAIL"} and not retryable_connection
            and not (extend_existing and state.get("status") == "PASS")
            or (retry_case_arg and not retry_target_allowed)
        ):
            raise SystemExit("Existing run is not resumable")
        state["status"] = "RUNNING"
    else:
        state = {
        "schema_version": 1, "experiment_id": "quality_checks_009",
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "RUNNING", "profile": PROFILE,
        "environment": {"os": "Windows", "python": sys.version.split()[0], "database": "isolated temporary SQLite"},
        "credential_source": "user-authorized API directory; values excluded",
        "configured_priority": configured, "logical_request_limit": MAX_LOGICAL,
        "provider_attempt_limit": MAX_PROVIDER, "logical_requests": 0, "app_generate_requests": 0,
        "provider_attempts": 0, "tests": [], "temporary_database_isolated": True,
        }
        state["smoke_scope"] = SMOKE_SCOPE
    save(state)
    with TestClient(app_module.app) as client:
        saved_profile = client.put("/api/profile", json={"content": json.dumps(PROFILE, ensure_ascii=False), "avoid": PROFILE["avoid"]})
        if saved_profile.status_code >= 400:
            state.update(status="FAIL", blocking_reason="Could not save fictional profile to isolated database")
            save(state)
            return 2
        completed_ids = {record.get("id") for record in state.get("tests", [])} if continuing else set()
        if continuing and retry_case_arg:
            retry_case = dict(retry_target, id=f"{retry_case_arg}_retry")
            cases_to_run = [retry_case]
        elif continuing and retry_smoke_once:
            retry_case = dict(CASES[0], id="smoke_reply_retry")
            cases_to_run = [retry_case] if retryable_connection else []
        else:
            cases_to_run = [case for case in CASES if case["id"] not in completed_ids] if continuing else (CASES[:1] if "--smoke-only" in sys.argv else CASES)
        for case in cases_to_run:
            if state["logical_requests"] >= MAX_LOGICAL or state["provider_attempts"] >= MAX_PROVIDER:
                state.update(status="BLOCKED", blocking_reason="Authorized live request ceiling reached")
                break
            response = client.post("/api/matches", json={"name": f"架空の相手_{case['id']}", "description": "旅行とカフェが好きな架空の相手です。落ち着いた店を探しています。"})
            if response.status_code != 201:
                state.update(status="FAIL", blocking_reason="Could not create fictional match in isolated database")
                break
            match_id = response.json()["id"]
            for role, message in case["history"] + [("them", case["latest"])]:
                added = client.post(f"/api/matches/{match_id}/messages", json={"role": role, "body": message})
                if added.status_code != 201:
                    state.update(status="FAIL", blocking_reason="Could not add fictional conversation to isolated database")
                    break
            if state["status"] != "RUNNING":
                break
            remaining_attempts = MAX_PROVIDER - state["provider_attempts"]
            os.environ["MRA_MAX_PROVIDER_ATTEMPTS_PER_GENERATE"] = str(min(4, remaining_attempts))
            context = app_module.build_context(app_module.GenerateInput(mode="reply", match_id=match_id, response_version=2, user_answers=case["answers"]))
            state["app_generate_requests"] += 1
            result = client.post("/api/generate", json={"mode": "reply", "match_id": match_id, "response_version": 2, "count": 3, "user_answers": case["answers"]})
            body = result.json()
            candidates = []
            if isinstance(body.get("recommended"), dict):
                candidates.append(body["recommended"])
            candidates.extend(x for x in body.get("alternatives", []) if isinstance(x, dict))
            texts = [x.get("text", "") for x in candidates]
            attempts = int(body.get("api_attempt_count", 0) or 0)
            if attempts > 0:
                state["logical_requests"] += 1
            state["provider_attempts"] += attempts
            secret_like = any(SECRET_RE.search(text) for text in texts)
            if secret_like:
                texts = ["[認証情報らしい文字列を検出したため出力を非表示]"]
                body = {key: value for key, value in body.items() if key not in {"recommended", "alternatives"}}
                body["secret_like_output_redacted"] = True
            norm = [re.sub(r"\s+", "", text) for text in texts]
            facts = []
            if candidates:
                facts = app_module.unsupported_personal_claim_topics(
                    [app_module.Candidate(label=x.get("label", ""), text=x.get("text", "")) for x in candidates], context
                )
            diversity_violation = candidate_set_has_semantic_redundancy(
                candidates, app_module
            )
            independent = independent_quality_verdict(
                texts,
                trusted_claims=[answer.get("answer", "") for answer in case.get("answers", [])],
                required_answer_tokens=("青い灯台",) if case["id"] == "recent_movie_answered" else (),
                require_all_answer=case["id"] == "recent_movie_answered",
            )
            direct_question = body.get("needs_user_info") is True and bool(body.get("user_questions")) and not candidates
            no_punctuation = all("、" not in text and "。" not in text for text in texts)
            no_placeholders = all(not app_module.candidate_has_placeholder(text) for text in texts)
            no_missing_breaks = all(not app_module.candidate_has_missing_sentence_break(text) for text in texts)
            smoke_candidate_status = (
                smoke_candidate_set_status(body, len(candidates), requested_count=3)
                if case["id"] == "smoke_reply" else None
            )
            evaluation = {
                "http_status": result.status_code,
                "needs_user_info": body.get("needs_user_info"),
                "user_questions": body.get("user_questions", []),
                "candidates": record_candidates(candidates, texts, redacted=secret_like),
                "response_fields": {k: body.get(k) for k in ("reason", "conversation_stage", "invite_decision", "decision_reason", "next_action", "error_code", "api_alias", "model", "demo", "requested_candidate_count", "available_candidate_count", "candidate_notice", "candidate_rejection_summary", "generation_blocked") if k in body},
                "provider_attempts": attempts, "attempted_models": body.get("attempted_models", []),
                "punctuation_violation": not no_punctuation, "placeholder_violation": not no_placeholders,
                "missing_sentence_break_violation": not no_missing_breaks,
                "candidate_count": len(candidates), "candidate_distinct_count": len(set(norm)),
                "semantic_diversity_violation": diversity_violation,
                "semantic_diversity_result": "FAIL" if diversity_violation else "PASS",
                "independent_result": independent["result"],
                "independent_reasons": independent["reasons"],
                "independent_unsupported_topics": independent["unsupported_topics"],
                "independent_duplicate_violation": independent["duplicate_violation"],
                "independent_redundant_reaction_violation": independent["redundant_reaction_violation"],
                "independent_answer_violation": independent["answer_violation"],
                **({"candidate_set_status": smoke_candidate_status} if smoke_candidate_status else {}),
                "unsupported_personal_claim_topics": facts,
                "text_lengths": [len(text) for text in texts],
                "sentence_estimates": [len([p for p in re.split(r"[!?！？]+|\n+", text.strip()) if p.strip()]) for text in texts],
                "logical_request": state["logical_requests"] if attempts > 0 else None,
                "app_generate_request": state["app_generate_requests"],
            }
            # Smoke verifies live generation and safe output. A safety-filtered
            # shortage remains distinct from a complete three-candidate set.
            content_pass = (result.status_code == 200 and body.get("demo") is False and len(candidates) >= 1 and not secret_like
                            and no_punctuation and no_placeholders and no_missing_breaks and len(set(norm)) == len(norm)
                            and not facts and body.get("generation_blocked") is not True)
            if case["id"] == "smoke_reply":
                content_pass = content_pass and smoke_has_live_valid_response(
                    body, len(candidates), requested_count=3, provider_attempts=attempts
                )
            if case["id"] == "direct_question_unconfirmed":
                content_pass = (result.status_code == 200 and direct_question and attempts == 0)
            if case["id"] == "recent_movie_answered":
                content_pass = content_pass and not independent["answer_violation"]
            if case["id"] == "respect_decline":
                content_pass = content_pass and body.get("invite_decision") in {"respect_no", "do_not_repeat_invite", "wait", "continue_or_close", "do_not_invite"}
            if case["id"] == "respect_decline_after_fix":
                content_pass = (
                    content_pass
                    and body.get("invite_decision") in {"respect_no", "do_not_repeat_invite", "wait", "continue_or_close", "do_not_invite"}
                    and any(text.strip() for text in texts)
                    and not any(app_module.candidate_has_meeting_related_question(text) for text in texts)
                )
            if case["id"] == "invite_opportunity" and body.get("invite_decision") == "invite_gently":
                content_pass = content_pass and any(
                    re.search(r"(?:よかったら|今度|一緒に).{0,30}(?:行きません|行ってみません|どうですか|行けたら)", text, re.S)
                    for text in texts
                )
            product_pass = content_pass and not diversity_violation
            independent_pass = independent["result"] == "PASS"
            evaluation["evaluator_divergence"] = product_pass and not independent_pass
            evaluation["result"] = combine_quality_verdict(
                product_pass,
                independent_pass,
                http_status=result.status_code,
                error_code=body.get("error_code"),
            )
            if content_pass and diversity_violation:
                evaluation["failure_notes"] = [
                    "The application's semantic-diversity checker found substantially similar candidate reactions or reply moves."
                ]
            elif not content_pass:
                if result.status_code >= 500 or body.get("error_code"):
                    evaluation["failure_notes"] = [
                        f"Provider/application request failed with classified code {body.get('error_code', 'http_error')}; no candidate was returned."
                    ]
                else:
                    evaluation["failure_notes"] = [
                        "Generated output was withheld or violated the content gates; no unsafe candidate was persisted or sent."
                    ]
            entry = {"id": case["id"], "input": {"latest_partner_message": case["latest"], "history": [{"role": role, "body": message} for role, message in case["history"]], "fictional_profile": PROFILE, "fictional_user_answers": case["answers"]}, "evaluation": evaluation}
            state["tests"].append(entry)
            save(state)
            if state["provider_attempts"] > MAX_PROVIDER:
                state.update(status="FAIL", blocking_reason="Application exceeded provider attempt budget; no further calls will be made")
                break
            if case["id"] == "smoke_reply" and content_pass:
                state["smoke"] = "PASS"
            elif case["id"] == "smoke_reply" and not content_pass:
                state.update(
                    status="BLOCKED" if body.get("error_code") else "FAIL",
                    blocking_reason=f"Initial smoke request unsuccessful: {body.get('error_code', 'incomplete_or_invalid_response')}",
                )
                break
            if body.get("error_code") or secret_like:
                state["status"] = "BLOCKED"
                state["blocking_reason"] = "Stopped after a provider, output safety, or generation error"
                break
    if state["status"] == "RUNNING" and "--smoke-only" in sys.argv:
        finalize_smoke_only_state(state)
    if state["status"] == "RUNNING":
        results_by_id = {
            item.get("id"): item.get("evaluation", {}).get("result")
            for item in state["tests"]
        }
        unresolved = []
        historical_nonpass_count = 0
        for item in state["tests"]:
            evaluation = item.get("evaluation", {})
            result = evaluation.get("result")
            if result not in {"FAIL", "BLOCKED"}:
                continue
            historical_nonpass_count += 1
            retry_id = f"{item.get('id')}_retry"
            if results_by_id.get(retry_id) == "PASS":
                evaluation["superseded_by"] = retry_id
                evaluation["resolution"] = "同じ入力を修正後に再実行しPASS。元の結果は履歴として保持。"
            else:
                unresolved.append(result)
        state["historical_nonpass_count"] = historical_nonpass_count
        state["unresolved_nonpass_count"] = len(unresolved)
        state["status"] = (
            "FAIL" if "FAIL" in unresolved else
            "BLOCKED" if "BLOCKED" in unresolved else
            "PASS" if state["tests"] else
            "FAIL"
        )
    state["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save(state)
    print(f"status={state['status']} logical_requests={state['logical_requests']} provider_attempts={state['provider_attempts']} output={OUTPUT.name} credentials=not_displayed")
    for entry in state["tests"]:
        ev = entry["evaluation"]
        print(f"{entry['id']}: {ev['result']} http={ev['http_status']} attempts={ev['provider_attempts']} model={ev.get('response_fields', {}).get('model')} alias={ev.get('response_fields', {}).get('api_alias')}")
        for candidate in ev.get("candidates", []):
            print(f"  {candidate['label']}: {candidate['text']}")
        if ev.get("user_questions"):
            print(f"  user_questions: {json.dumps(ev['user_questions'], ensure_ascii=False)}")
    return quality_run_exit_code(state["status"])


if __name__ == "__main__":
    raise SystemExit(main())
