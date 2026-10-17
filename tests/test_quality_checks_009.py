from scripts.run_quality_checks_009 import (
    CASES,
    SMOKE_SCOPE,
    quality_case_result,
    quality_run_exit_code,
    record_candidates,
    finalize_smoke_only_state,
    smoke_candidate_set_status,
    smoke_has_live_valid_response,
)


def test_saved_quality009_live_candidates_replay_through_current_safety_filter(tmp_path, monkeypatch):
    """Preserve original live text while checking current candidate safeguards."""
    import importlib.util
    import json
    from pathlib import Path
    import sys

    root = Path(__file__).parents[1]
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MRA_API_DIR", str(tmp_path / "empty-api"))
    monkeypatch.setenv("MRA_PROVIDER_MIN_INTERVAL_SECONDS", "0")
    monkeypatch.delenv("MRA_API_1_KEY", raising=False)
    monkeypatch.delenv("MRA_API_2_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    spec = importlib.util.spec_from_file_location("quality009_replay_backend", root / "app.py")
    assert spec is not None and spec.loader is not None
    backend = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, backend)
    spec.loader.exec_module(backend)
    report_path = root / "docs/verification/simulations/quality_checks_009.json"
    saved = json.loads(report_path.read_text(encoding="utf-8"))
    cases = {item["id"]: item for item in saved["tests"]}
    expected_rejections = {
        "short_mirroring": {"話題の展開": "明らかな誤字"},
        "recent_movie_answered": {
            "代替案1": "相手からの直接質問に未回答",
            "代替案2": "相手からの直接質問に未回答",
        },
        "answered_purchase_fact": {
            "調べてから買う派として答える": "未確認の本人事実",
        },
        "known_partner_fact": {"代替2": "未確認の本人事実"},
        "respect_decline_after_fix": {"距離を置いた共感": "相手の不安を軽く扱う表現"},
    }

    for case_id, rejected_labels in expected_rejections.items():
        case = cases[case_id]
        source_candidates = case["evaluation"]["candidates"]
        candidate_models = [
            backend.Candidate(label=item["label"], text=item["text"])
            for item in source_candidates
        ]
        fields = case["evaluation"]["response_fields"]
        suggestions = backend.SuggestionsV2(
            needs_user_info=False,
            user_questions=[],
            user_info_reason="",
            recommended=candidate_models[0],
            alternatives=candidate_models[1:],
            reason=fields.get("reason") or "保存済み実生成応答",
            strategy=fields.get("strategy") or "",
            conversation_stage=fields.get("conversation_stage") or "Stage 2",
            invite_decision=fields.get("invite_decision") or "continue_conversation",
            decision_reason=fields.get("decision_reason") or "",
            next_action=fields.get("next_action") or "",
        )
        history = list(case["input"].get("history") or [])
        history.append({"role": "them", "body": case["input"]["latest_partner_message"]})
        context = {
            "mode": "reply",
            "history": history,
            "my_profile": {"facts": case["input"].get("fictional_profile") or {}},
            "ephemeral_user_answers": case["input"].get("fictional_user_answers") or [],
        }

        filtered = backend.filter_safe_candidates(suggestions, 3, context)
        actual_rejections = {
            item["label"]: item["reasons"]
            for item in filtered["candidate_rejections"]
        }
        for label, reason in rejected_labels.items():
            assert reason in actual_rejections.get(label, [])
        assert filtered["available_candidate_count"] >= 1
        assert filtered["generation_blocked"] is False

        retained_texts = {
            item["text"]
            for item in [filtered["recommended"], *filtered["alternatives"]]
        }
        assert retained_texts <= {item["text"] for item in source_candidates}


def test_smoke_quality_distinguishes_complete_and_safe_partial_candidate_sets():
    assert smoke_candidate_set_status(
        {"needs_user_info": False, "demo": False}, actual_count=3, requested_count=3
    ) == "complete"
    assert smoke_candidate_set_status(
        {"needs_user_info": False, "demo": False}, actual_count=2, requested_count=3
    ) == "partial_safe"
    assert smoke_candidate_set_status(
        {"needs_user_info": True, "demo": False}, actual_count=0, requested_count=3
    ) == "not_applicable"
    assert smoke_candidate_set_status(
        {"needs_user_info": False, "demo": True}, actual_count=3, requested_count=3
    ) == "not_applicable"
    assert smoke_candidate_set_status(
        {"needs_user_info": False, "demo": False}, actual_count=0, requested_count=3
    ) == "invalid"


def test_smoke_pass_requires_provider_attempt_and_model_identity():
    response = {
        "needs_user_info": False,
        "demo": False,
        "model": "gemini-fictional-test-model",
    }
    assert smoke_has_live_valid_response(response, 2, 3, provider_attempts=1)
    assert not smoke_has_live_valid_response(response, 2, 3, provider_attempts=0)
    assert not smoke_has_live_valid_response(
        {**response, "model": None}, 2, 3, provider_attempts=1
    )
    assert not smoke_has_live_valid_response(
        {**response, "demo": True}, 3, 3, provider_attempts=1
    )


def test_quality_record_preserves_candidate_reply_moves():
    recorded = record_candidates(
        [
            {"label": "自然な反応", "reply_move": "react"},
            {"label": "話題を広げる", "reply_move": "expand"},
        ],
        ["短い反応です！", "次の話題につなげます！"],
        redacted=False,
    )

    assert [item["reply_move"] for item in recorded] == ["react", "expand"]
    assert [item["text"] for item in recorded] == ["短い反応です！", "次の話題につなげます！"]
    assert record_candidates([{"label": "秘密", "reply_move": "react"}], ["secret"], redacted=True) == []


def test_fictional_movie_fixture_does_not_put_test_label_in_user_answer():
    case = next(item for item in CASES if item["id"] == "recent_movie_answered")
    answer = case["answers"][0]["answer"]

    assert answer == "最近は『青い灯台』を観ました"
    assert "架空作品" not in answer


def test_semantically_redundant_live_candidates_fail_quality_verdict():
    assert quality_case_result(
        content_pass=True,
        diversity_violation=True,
        http_status=200,
        error_code=None,
    ) == "FAIL"
    assert quality_case_result(
        content_pass=True,
        diversity_violation=False,
        http_status=200,
        error_code=None,
    ) == "PASS"
    assert quality_case_result(
        content_pass=False,
        diversity_violation=False,
        http_status=502,
        error_code="gemini_error",
    ) == "BLOCKED"


def test_smoke_only_status_matches_semantic_quality_verdict_and_exit_code():
    redundant_safe_live_response = {
        "smoke": "PASS",
        "tests": [{"id": "smoke_reply", "evaluation": {"result": "FAIL"}}],
    }
    finalize_smoke_only_state(redundant_safe_live_response)
    assert redundant_safe_live_response["status"] == "FAIL"
    assert "excludes semantic diversity" in redundant_safe_live_response["smoke_scope"]
    assert quality_run_exit_code(redundant_safe_live_response["status"]) == 2

    quality_pass = {
        "smoke": "PASS",
        "tests": [{"id": "smoke_reply", "evaluation": {"result": "PASS"}}],
    }
    finalize_smoke_only_state(quality_pass)
    assert quality_pass["status"] == "SMOKE_PASS"
    assert quality_run_exit_code(quality_pass["status"]) == 0

    blocked = {"smoke": "NOT_RUN", "blocking_reason": "provider unavailable", "tests": []}
    finalize_smoke_only_state(blocked)
    assert blocked["status"] == "BLOCKED"
    assert quality_run_exit_code(blocked["status"]) == 2


def test_smoke_scope_is_explicit_for_full_and_smoke_only_artifacts():
    assert "excludes semantic diversity" in SMOKE_SCOPE


def test_output_path_can_be_redirected_without_overwriting_the_record(tmp_path, monkeypatch):
    import importlib.util
    import sys
    from pathlib import Path

    root = Path(__file__).parents[1]
    target = tmp_path / "quality_checks_009_20261017.json"
    monkeypatch.setenv("MRA_QUALITY_OUTPUT", str(target))
    spec = importlib.util.spec_from_file_location(
        "quality009_output_override", root / "scripts/run_quality_checks_009.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)

    assert module.OUTPUT == target
    assert module.OUTPUT != root / "docs/verification/simulations/quality_checks_009.json"
