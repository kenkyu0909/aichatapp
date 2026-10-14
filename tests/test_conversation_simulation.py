"""Offline safety tests for the fictional conversation harness."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("simulate_conversation", ROOT / "scripts" / "simulate_conversation.py")
simulation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(simulation)


def state_with_sent(count=0):
    state = simulation.new_state()
    state["app_sent_count"] = count
    state["status"] = "RUNNING"
    return state


def test_app_message_limit_counts_only_sent_messages():
    state = state_with_sent(19)
    assert simulation.can_send_app(state)
    turn = {"candidates": [{"text": "候補"}]}
    assert simulation.send_app_message(state, "実際に送る文", turn) == 20
    assert state["app_sent_count"] == 20
    assert not simulation.can_send_app(state)
    with pytest.raises(RuntimeError):
        simulation.send_app_message(state, "21通目", {})


def test_partner_and_unselected_candidates_do_not_increment_app_counter():
    state = simulation.new_state()
    assert simulation.can_send_app(state)
    state["turns"].append({"candidates": [{"text": "未送信候補"}], "selected_text": None})
    simulation.send_partner_message(state, "架空の相手からの返事")
    assert state["app_sent_count"] == 0


@pytest.mark.parametrize("status", ["SUCCESS", "SAFETY_STOP", "BLOCKED"])
def test_terminal_state_prevents_app_send(status):
    state = state_with_sent(2)
    state["status"] = status
    assert not simulation.can_send_app(state)
    with pytest.raises(RuntimeError):
        simulation.send_app_message(state, "送信できない文", {})


def test_report_escapes_profile_and_message_html(tmp_path):
    state = simulation.new_state()
    state["status"] = "BLOCKED"
    state["people"]["partner_public"]["profile"] = '<img src=x onerror="alert(1)">'
    state["messages"].append({"sequence": 1, "speaker": "partner", "body": "<script>alert(1)</script>"})
    target = tmp_path / "report.html"
    simulation.render_html(state, target)
    document = target.read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in document
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in document
    assert '<img src=x onerror="alert(1)">' not in document
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in document


def test_model_priority_and_only_rate_limit_advances():
    assert simulation.MODEL_ORDER == (
        ("API1", "gemini-3.5-flash-lite"),
        ("API2", "gemini-3.5-flash-lite"),
        ("API1", "gemini-3.1-flash-lite"),
        ("API2", "gemini-3.1-flash-lite"),
    )
    assert simulation.fallback_slot(True, 0) == 1
    assert simulation.fallback_slot(True, 2) == 3
    assert simulation.fallback_slot(False, 0) is None
    assert simulation.fallback_slot(True, 3) is None


def test_meeting_success_requires_concrete_proposal_and_acceptance():
    proposal = "よかったら土曜日の18時に横浜駅近くのカフェへ行きませんか？"
    assert simulation.has_concrete_meeting_agreement(proposal, "いいですね、大丈夫です！")
    assert not simulation.has_concrete_meeting_agreement(proposal, "ごめんなさい、難しいです")
    assert not simulation.has_concrete_meeting_agreement(proposal, "いいですね。ただ予定がまだ分からないので、決めるのは後でもいいです")
    assert not simulation.has_concrete_meeting_agreement("今度会いませんか？", "ぜひ！")


def test_success_requires_explicit_confirmation_after_saved_partner_reply():
    state = simulation.new_state()
    state["messages"] = [
        {"speaker": "app", "body": "土曜日の18時に横浜駅のカフェへ行きませんか？"},
        {"speaker": "partner", "body": "いいですね、大丈夫です！"},
    ]
    state["pending_meeting_confirmation"] = {
        "proposal": state["messages"][0]["body"],
        "acceptance": state["messages"][1]["body"],
    }
    assert state["status"] == "RUNNING"
    simulation.confirm_meeting_success(state)
    assert state["status"] == "SUCCESS"
    assert all(m["meeting_agreement"] for m in state["messages"])


def test_profile_export_keeps_counterpart_internal_separate(tmp_path):
    target = tmp_path / "profiles.md"
    simulation.export_profiles(target)
    text = target.read_text(encoding="utf-8")
    assert "公開プロフィール" in text
    assert "内部設定（Codexのみ" in text
    assert "アプリ/Geminiには送信しない" in text
