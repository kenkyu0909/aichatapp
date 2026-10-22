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
from fastapi.testclient import TestClient


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
    (
        "最近もカフェに行きましたか？",
        context(history=[{"role": "them", "body": "カフェ巡りが好きで最近もカフェに行きました！"}]),
    ),
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
    assert result.get("requested_candidate_count") == 2
    assert result.get("available_candidate_count") == 0
    assert result.get("candidate_notice")
    assert (
        result.get("error")
        or result.get("error_code")
        or result.get("generation_blocked") is True
        or result.get("detail")
    )


def test_filter_scans_past_unsafe_candidates_and_obeys_requested_count_one(backend):
    safe_first = "そのお店の雰囲気気になります！"
    safe_second = "最近行ったカフェのお話を聞いてみたいです！"
    value = make_suggestions(
        backend,
        "そうなんですね。楽しそうです！",
        safe_first,
        safe_second,
    )

    result = backend.filter_safe_candidates(value, 1, context())

    candidates = unpack_candidates(result)
    assert [item["text"] for item in candidates] == [safe_first]
    assert result["requested_candidate_count"] == 1
    assert result["available_candidate_count"] == 1
    assert result["candidate_rejections"]
    assert result["candidate_rejections"][0]["label"] == "候補1"


def test_filter_keeps_safe_but_near_duplicate_candidates_and_warns(backend):
    first = "カフェ巡りいいですね！\n最近行ったお店はありますか？"
    second = "カフェ巡りいいですね！\n最近行ったお店ってありますか？"
    value = make_suggestions(backend, first, second)

    result = backend.filter_safe_candidates(value, 2, context())

    assert [item["text"] for item in unpack_candidates(result)] == [first, second]
    assert result["available_candidate_count"] == 2
    assert "似ている可能性" in result["candidate_notice"]


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


def test_filter_keeps_answer_to_known_purchase_question_and_drops_candidates_that_evade_it(backend):
    answer = {
        "question": "気になる新作を見つけたらすぐ買うタイプですか？",
        "answer": "少し調べてから買うことが多いです",
    }
    safe_text = "少し調べてから買うことが多いです！"
    value = make_suggestions(
        backend,
        "新作って見ているだけでも楽しいですよね！",
        safe_text,
    )
    ctx = context(answers=[answer], history=[{
        "role": "them",
        "body": answer["question"],
    }])

    result = backend.filter_safe_candidates(value, 2, ctx)

    candidates = unpack_candidates(result)
    assert [item["text"] for item in candidates] == [safe_text]
    assert result["requested_candidate_count"] == 2
    assert result["available_candidate_count"] == 1
    assert "不足分を不自然な候補で補っていません" in result["candidate_notice"]


def test_filter_drops_unsupported_partner_work_assumption(backend):
    value = make_suggestions(backend, "お仕事お疲れ様です！")

    result = backend.filter_safe_candidates(
        value,
        1,
        context(other_description="読書と旅行が好きです"),
    )

    assert unpack_candidates(result) == []


def test_generate_exposes_requested_count_and_notice_when_all_candidates_are_blocked(
    backend, monkeypatch
):
    from google import genai

    payload = {
        "needs_user_info": False,
        "user_questions": [],
        "user_info_reason": "",
        "recommended": {"label": "自然", "text": "そうなんですね。それは楽しそうです！"},
        "alternatives": [
            {"label": "別案", "text": "〇〇さんはどうですか？"},
            {"label": "質問", "text": "なるほど。最近はどうですか？"},
        ],
        "reason": "架空データのオフライン検証",
        "strategy": "相手の話題に沿って返信する",
        "conversation_stage": "Stage 2",
        "invite_decision": "continue_conversation",
        "decision_reason": "会話を続ける",
        "next_action": "会話を続ける",
    }
    calls = []

    class FakeModels:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return type("Response", (), {"text": json.dumps(payload, ensure_ascii=False)})()

    monkeypatch.setattr(
        backend,
        "gemini_configurations",
        lambda: [("API1", "offline-placeholder-key", "offline-model")],
    )
    monkeypatch.setattr(
        genai,
        "Client",
        lambda **kwargs: type("FakeClient", (), {"models": FakeModels()})(),
    )

    with TestClient(backend.app) as client:
        created = client.post(
            "/api/matches",
            json={"name": "架空の相手", "description": "カフェ巡りが好きです"},
        )
        assert created.status_code == 201
        match_id = created.json()["id"]
        assert client.post(
            f"/api/matches/{match_id}/messages",
            json={"role": "them", "body": "カフェに行きました！"},
        ).status_code == 201

        response = client.post(
            "/api/generate",
            json={"mode": "reply", "match_id": match_id, "count": 3, "response_version": 2},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["generation_blocked"] is True
    assert body["recommended"] is None
    assert body["alternatives"] == []
    assert body["requested_candidate_count"] == 3
    assert body["available_candidate_count"] == 0
    assert body["candidate_notice"]
    assert len(calls) == 2  # one constrained repair, no unbounded retry


def test_verified_movie_title_can_be_used_without_exact_answer_copy(backend):
    context = {
        "my_profile": {"facts": {}},
        "history": [{"role": "them", "body": "最近どんな映画を観ましたか？"}],
        "ephemeral_user_answers": [{
            "question": "最近観た映画の作品名を教えてください",
            "answer": "最近は架空作品の『青い灯台』を観ました",
        }],
    }
    candidate = backend.Candidate(
        label="最近の映画の話題",
        text="『青い灯台』を観たんですね！\nどんなところが印象に残りましたか？",
    )

    assert backend._answers_verified_partner_question(candidate, context)
    assert backend.unsupported_personal_claim_topics([candidate], context) == []


def test_verified_movie_title_does_not_support_a_different_title(backend):
    context = {
        "my_profile": {"facts": {}},
        "history": [{"role": "them", "body": "最近どんな映画を観ましたか？"}],
        "ephemeral_user_answers": [{
            "question": "最近観た映画の作品名を教えてください",
            "answer": "最近は架空作品の『青い灯台』を観ました",
        }],
    }
    candidate = backend.Candidate(label="別作品", text="『冬の灯り』を観ました！")

    assert not backend._answers_verified_partner_question(candidate, context)
