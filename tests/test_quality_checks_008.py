"""Offline candidate-level safety tests for quality rebuild 008.

These tests never contact Gemini. They exercise the planned public backend
filter with fictional candidates and a temporary application data directory.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture
def backend(tmp_path, monkeypatch) -> ModuleType:
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / "isolated-data"))
    monkeypatch.setenv("MRA_API_DIR", str(tmp_path / "empty-api"))
    monkeypatch.setenv("MRA_PROVIDER_MIN_INTERVAL_SECONDS", "0")
    for name in ("MRA_API_1_KEY", "MRA_API_2_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(name, raising=False)

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("test_quality_checks_008_backend", app_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def make_suggestions(backend: ModuleType, *texts: str):
    assert texts
    return backend.SuggestionsV2.model_validate({
        "needs_user_info": False,
        "user_questions": [],
        "user_info_reason": "",
        "recommended": {"label": "候補1", "text": texts[0]},
        "alternatives": [
            {"label": f"候補{index}", "text": text}
            for index, text in enumerate(texts[1:], start=2)
        ],
        "reason": "架空データのオフライン検証",
        "strategy": "相手の話題に沿って返信する",
        "conversation_stage": "Stage 2",
        "invite_decision": "continue_conversation",
        "decision_reason": "",
        "next_action": "会話を続ける",
    })


def unpack_candidates(result: dict) -> list[dict]:
    recommended = result.get("recommended")
    candidates = [recommended] if isinstance(recommended, dict) else []
    alternatives = result.get("alternatives", [])
    assert isinstance(alternatives, list)
    candidates.extend(item for item in alternatives if isinstance(item, dict))
    return candidates


def context(*, facts=None, answers=None, history=None, other_description="旅行と読書が好きです"):
    return {
        "my_profile": {"facts": facts or {}},
        "ephemeral_user_answers": answers or [],
        "history": history or [],
        "other": {"name": "架空の相手", "description": other_description},
    }


@pytest.mark.parametrize(("unsafe_text", "ctx"), [
    ("そうなんですね。楽しそうです！", context()),
    ("〇〇さんはどんな映画が好きですか？", context()),
    ("カフェ巡りいいですね！\n\n最近行ったお店ありますか？", context()),
    ("カフェ好きなんですね！最近行きましたか？", context()),
    (
        "友達とカフェに行くことが多いんですか？",
        context(history=[{"role": "them", "body": "休日は友達とカフェに行くことが多いです！"}]),
    ),
    ("私も映画が好きです！", context()),
    (
        "私も新作はすぐ買うタイプです！",
        context(answers=[{
            "question": "気になる新作を見つけたらすぐ買うタイプですか？",
            "answer": "少し調べてから買うことが多いです",
        }]),
    ),
    ("お仕事お疲れ様です！", context(other_description="読書と旅行が好きです")),
])
def test_filter_drops_each_unsafe_candidate_but_keeps_safe_candidates(backend, unsafe_text, ctx):
    safe_text = "その話気になります！"
    value = make_suggestions(backend, unsafe_text, safe_text)

    result = backend.filter_safe_candidates(value, 2, ctx)

    assert isinstance(result, dict)
    candidates = unpack_candidates(result)
    assert [item["text"] for item in candidates] == [safe_text]


def test_filter_does_not_pad_safe_candidates_to_requested_count(backend):
    first = "そのお店の雰囲気気になります！"
    second = "ケーキのお話も楽しそうですね！"
    value = make_suggestions(
        backend,
        "そうなんですね。楽しそうです！",
        first,
        second,
    )

    result = backend.filter_safe_candidates(value, 3, context())

    candidates = unpack_candidates(result)
    assert [item["text"] for item in candidates] == [first, second]
    assert len({item["text"] for item in candidates}) == 2
    assert len(candidates) < 3


def test_filter_returns_explicit_empty_result_when_every_candidate_is_unsafe(backend):
    value = make_suggestions(
        backend,
        "そうなんですね。楽しそうです！",
        "〇〇さんはどうですか？",
    )

    result = backend.filter_safe_candidates(value, 2, context())

    assert isinstance(result, dict)
    assert unpack_candidates(result) == []
    assert result.get("recommended") is None
    assert result.get("alternatives") == []
    assert (
        result.get("error")
        or result.get("error_code")
        or result.get("generation_blocked") is True
        or result.get("detail")
    )


@pytest.mark.parametrize(("facts", "answers", "candidate_text"), [
    (
        {"movie_preferences": ["映画が好き"]},
        [],
        "映画が好きです！",
    ),
    (
        {},
        [{"question": "映画は好きですか？", "answer": "映画は好きです！"}],
        "映画は好きです！",
    ),
    (
        {"shopping_habits": "新作は少し調べてから買うことが多い"},
        [],
        "新作は少し調べてから買うことが多いです！",
    ),
])
def test_filter_keeps_personal_facts_supported_by_profile_or_temporary_answer(
    backend, facts, answers, candidate_text
):
    value = make_suggestions(backend, candidate_text)

    result = backend.filter_safe_candidates(
        value,
        1,
        context(facts=facts, answers=answers),
    )

    assert [item["text"] for item in unpack_candidates(result)] == [candidate_text]


def test_filter_drops_movie_preference_when_profile_has_no_movie_fact(backend):
    value = make_suggestions(backend, "映画は好きです！")

    result = backend.filter_safe_candidates(value, 1, context())

    assert unpack_candidates(result) == []


def test_filter_drops_purchase_claim_that_conflicts_with_confirmed_answer(backend):
    value = make_suggestions(backend, "新作はすぐ買うことが多いです！")

    result = backend.filter_safe_candidates(
        value,
        1,
        context(answers=[{
            "question": "気になる新作を見つけたらすぐ買うタイプですか？",
            "answer": "少し調べてから買うことが多いです",
        }]),
    )

    assert unpack_candidates(result) == []


def test_filter_drops_unsupported_partner_work_assumption(backend):
    value = make_suggestions(backend, "お仕事お疲れ様です！")

    result = backend.filter_safe_candidates(
        value,
        1,
        context(other_description="読書と旅行が好きです"),
    )

    assert unpack_candidates(result) == []
