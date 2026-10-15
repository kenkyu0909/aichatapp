from scripts.run_quality_checks_009 import (
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
