"""Offline checks for the bounded live quality-check runner."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_quality_checks_006.py"
SPEC = importlib.util.spec_from_file_location("mra_quality_checks_006", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
quality = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quality)


def test_quality_check_006_has_eight_bounded_live_requests_and_covers_required_gates():
    assert quality.MAX_LOGICAL_REQUESTS == 8
    assert len(quality.FACT_CASES) + len(quality.QUALITY_CASES) == 8
    case_ids = {case["id"] for case in quality.FACT_CASES + quality.QUALITY_CASES}
    assert {
        "reading_genre_answered",
        "recent_movie_answered",
        "purchase_habit_answered",
        "respect_decline_and_no_reask",
        "placeholder_free",
        "invite_opportunity",
        "newline_per_sentence",
        "empathy_variety",
    } == case_ids


def test_quality_check_006_requires_exact_provider_priority_without_secret_values():
    configured = [
        {"api_alias": alias, "model": model}
        for alias, model in quality.REQUIRED_PROVIDER_PRIORITY
    ]
    assert quality.provider_priority_matches(configured)
    assert not quality.provider_priority_matches(configured[1:] + configured[:1])


def test_quality_check_006_fact_answer_evaluation_accepts_semantic_markers():
    assert quality.answer_fact_is_present(
        "ミステリーを読むことが多いです！\n最近は青い灯台を観ました",
        ["ミステリー", "読むことが多い"],
    )


def test_quality_check_006_requires_at_least_one_candidate_to_use_answer_facts():
    candidates = [
        {"text": "ミステリーを読むことが多いです！"},
        {"text": "最近読んだ本はありますか？"},
        {"text": "普段読むジャンルは何ですか？"},
    ]
    assert quality.at_least_one_candidate_uses_answer_facts(candidates, ["ミステリー", "読むことが多い"])
    assert not quality.at_least_one_candidate_uses_answer_facts(
        candidates[1:], ["ミステリー", "読むことが多い"]
    )


def test_quality_check_006_decline_case_rejects_invites_and_repeated_known_facts():
    safe = {
        "invite_decision": "respect_no",
        "candidates": [{"text": "不安な気持ちを教えてくれてありがとうございます\n無理に会おうとは思っていないので大丈夫です"}],
        "repeated_partner_fact_topics": [],
    }
    assert quality.decline_and_no_reask_is_safe(safe)
    for invitation in (
        "よかったら今度一緒にカフェに行きませんか？",
        "今度会いませんか？",
        "カフェでもご一緒しませんか？",
    ):
        inviting = {**safe, "candidates": [{"text": invitation}]}
        assert not quality.decline_and_no_reask_is_safe(inviting)
    cafe_conversation = {**safe, "candidates": [{"text": "カフェの話をしませんか？"}]}
    assert quality.decline_and_no_reask_is_safe(cafe_conversation)
    repeating = {**safe, "repeated_partner_fact_topics": ["友達とカフェに行く頻度"]}
    assert not quality.decline_and_no_reask_is_safe(repeating)
    pushy_decision = {**safe, "invite_decision": "invite_gently"}
    assert not quality.decline_and_no_reask_is_safe(pushy_decision)
    non_pushy_alternative_decision = {**safe, "invite_decision": "continue_or_close"}
    assert quality.decline_and_no_reask_is_safe(non_pushy_alternative_decision)


def test_quality_check_006_selects_only_explicit_api_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("MRA_API_1_KEY", "do-not-print-one")
    monkeypatch.setenv("MRA_API_2_KEY", "do-not-print-two")
    monkeypatch.setenv("GEMINI_API_KEY", "do-not-print-legacy")
    quality.select_authorized_api_source(tmp_path)
    assert os.environ["MRA_API_DIR"] == str(tmp_path.resolve())
    assert os.environ["MRA_API_1_KEY"] == ""
    assert os.environ["MRA_API_2_KEY"] == ""
    assert os.environ["GEMINI_API_KEY"] == ""
