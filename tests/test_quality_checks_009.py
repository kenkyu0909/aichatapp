from scripts.run_quality_checks_009 import (
    CASES,
    record_candidates,
    smoke_candidate_set_status,
    smoke_has_live_valid_response,
)


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
