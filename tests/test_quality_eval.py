"""Offline tests for the independent quality grader (item D09).

These assert that the grader is genuinely independent of ``app.py`` and that it
catches the failure modes the product-internal grader could miss.
"""
from pathlib import Path

import pytest

from scripts import quality_eval


def test_runner_009_wires_the_independent_grader():
    from scripts import run_quality_checks_009 as runner

    source = Path(runner.__file__).read_text(encoding="utf-8")
    assert "independent_quality_verdict(" in source
    assert "combine_quality_verdict(" in source
    assert "def quality_case_result(" in source


def test_quality_eval_module_imports_no_app():
    source = Path(quality_eval.__file__).read_text(encoding="utf-8")
    assert "import app\n" not in source
    assert "from app import" not in source
    assert "spec_from_file_location" not in source
    assert quality_eval.__dict__.get("app") is None


def test_independent_grader_flags_every_movie_nonanswer():
    texts = [
        "青い灯台という映画の話をしました",
        "映画が好きなんですね",
        "ほかの話題で盛り上がりましょう",
    ]
    verdict = quality_eval.independent_quality_verdict(
        texts, required_answer_tokens=["青い灯台"], require_all_answer=True
    )
    assert verdict["answer_violation"] is True
    assert verdict["result"] == "FAIL"
    assert "answer_missing_in_some_candidate" in verdict["reasons"]


def test_independent_grader_accepts_all_candidate_answers():
    texts = [
        "青い灯台という映画の話をしました",
        "青い灯台は評判がいいですね",
    ]
    verdict = quality_eval.independent_quality_verdict(
        texts, required_answer_tokens=["青い灯台"], require_all_answer=True
    )
    assert verdict["answer_violation"] is False
    assert verdict["result"] == "PASS"


def test_independent_grader_flags_unverified_first_person_claim():
    texts = ["私も映画が好きです"]
    assert quality_eval.untrusted_first_person_topics(texts) == ["映画"]
    verdict = quality_eval.independent_quality_verdict(texts)
    assert "unsupported_first_person_claim" in verdict["reasons"]


def test_independent_grader_accepts_grounded_claim():
    texts = ["私は映画が好きです"]
    assert quality_eval.untrusted_first_person_topics(texts, ["映画が好き"]) == []
    verdict = quality_eval.independent_quality_verdict(texts, trusted_claims=["映画が好き"])
    assert verdict["unsupported_topics"] == []
    assert verdict["result"] == "PASS"


def test_independent_grader_ignores_interrogative_first_person():
    assert quality_eval.untrusted_first_person_topics(["私は映画が好きですか"]) == []


def test_independent_grader_detects_near_duplicate_candidates():
    texts = ["とても楽しい時間でしたね", "とても楽しい時間でしたね"]
    assert quality_eval.has_near_duplicate_candidates(texts) is True
    verdict = quality_eval.independent_quality_verdict(texts)
    assert verdict["duplicate_violation"] is True


def test_independent_grader_allows_distinct_candidates():
    texts = ["映画が好きなんですね", "週末はどこに行くんですか"]
    assert quality_eval.has_near_duplicate_candidates(texts) is False
    assert quality_eval.has_redundant_reaction_set(texts) is False


def test_independent_grader_detects_redundant_reactions():
    texts = ["いいですね", "いいですね"]
    assert quality_eval.has_redundant_reaction_set(texts) is True


def test_independent_placeholder_and_punctuation_checks():
    assert quality_eval.has_placeholder("〇〇さん、こんにちは") is True
    assert quality_eval.has_placeholder("こんにちは") is False
    flagged = quality_eval.independent_quality_verdict(["こんにちは、元気ですか"])
    assert flagged["punctuation_violation"] is True
    assert flagged["result"] == "FAIL"
    clean = quality_eval.independent_quality_verdict(["こんにちは\n元気ですか"])
    assert clean["punctuation_violation"] is False


def test_independent_grader_matches_recorded_punctuation_free_candidates():
    texts = [
        "友達とカフェ巡りいいですね\nどんな雰囲気のお店に行ったんですか？",
        "カフェ巡り楽しそうですね\n最近お気に入りのエリアはありますか？",
    ]
    verdict = quality_eval.independent_quality_verdict(texts)
    assert verdict["punctuation_violation"] is False
    assert verdict["result"] == "PASS"


def test_independent_grader_flags_long_unbroken_text():
    long_text = "あ" * 50
    assert quality_eval.has_missing_sentence_break(long_text) is True
    assert quality_eval.has_missing_sentence_break("短いです。") is False


@pytest.mark.parametrize(
    ("product_pass", "independent_pass", "http_status", "error_code", "expected"),
    [
        (True, True, 200, None, "PASS"),
        (True, False, 200, None, "FAIL"),
        (False, True, 200, None, "FAIL"),
        (False, False, 200, None, "FAIL"),
        (True, True, 502, "provider_unavailable", "BLOCKED"),
        (True, True, 429, "request_attempt_limit", "BLOCKED"),
    ],
)
def test_combine_quality_verdict(product_pass, independent_pass, http_status, error_code, expected):
    assert quality_eval.combine_quality_verdict(
        product_pass, independent_pass, http_status=http_status, error_code=error_code
    ) == expected
