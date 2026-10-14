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


def test_conversation_002_has_isolated_paths_and_preserves_001():
    json_path, html_path, data_dir = simulation.experiment_paths("conversation_002")
    assert json_path.name == "conversation_002.json"
    assert html_path.name == "conversation_002.html"
    assert data_dir.name == "mra-conversation-002-sandbox"
    assert simulation.experiment_paths("conversation_001") == (
        simulation.JSON_FILE, simulation.HTML_FILE, simulation.DATA_DIR
    )
    with pytest.raises(ValueError):
        simulation.experiment_paths("../../conversation_001")
    state = simulation.new_state("conversation_002")
    assert state["people"]["app_user"]["age"] >= 20
    assert state["people"]["partner_public"]["age"] >= 20
    assert "Codexだけ" in state["people"]["partner_internal"]
    assert simulation.generation_settings(7, "自然に会話を広げる", "", "first")["mode"] == "first"
    assert simulation.generation_settings(7, "自然に会話を広げる", "")["mode"] == "reply"
    assert not simulation.needs_partner_opening(state, "first")
    assert simulation.needs_partner_opening(state, "reply")


def test_conversation_003_is_newly_isolated_and_has_mirroring_metrics():
    paths = simulation.experiment_paths("conversation_003")
    assert [path.name for path in paths[:2]] == ["conversation_003.json", "conversation_003.html"]
    assert paths[2].name == "mra-conversation-003-sandbox"
    assert simulation.experiment_paths("conversation_002")[:2] == (
        simulation.SIM_DIR / "conversation_002.json", simulation.SIM_DIR / "conversation_002.html"
    )
    state = simulation.new_state("conversation_003")
    assert state["people"]["app_user"]["age"] >= 20
    assert state["people"]["partner_public"]["age"] >= 20
    assert simulation.needs_partner_opening(state, "first") is False
    assert simulation.sentence_estimate("カフェ好きです！") == 1
    assert simulation.sentence_estimate("休日は友達とカフェへ行きました！\n新しいお店も探しています") >= 2
    simulation.send_partner_message(state, "カフェ好きです！")
    turn = {"candidates": [
        {"label": "A", "text": "カフェ好きなんですね！"},
        {"label": "B", "text": "どんなお店に行きますか？"},
        {"label": "C", "text": "最近気になるお店ありますか？"},
    ]}
    simulation.send_app_message(state, "どんなお店に行きますか？", turn)
    measured = turn["measured"]
    assert measured["partner_latest_character_count"] == len("カフェ好きです！")
    assert measured["selected_character_count"] == len("どんなお店に行きますか？")
    assert measured["punctuation_violation"] is False
    assert measured["acknowledgment_type_estimate"] == "相槌なし/その他"
    assert turn["reviewer_assessment"]["mirroring"] == "未評価"


def test_profile_export_does_not_overwrite_existing_snapshot_on_resume(tmp_path):
    profile_path = tmp_path / "profiles_003.md"
    simulation.export_profiles(path=profile_path, experiment_id="conversation_003")
    initial = profile_path.read_text(encoding="utf-8")
    assert "本人役" in initial and "相手役" in initial
    edited = initial + "\n再開時に保持するメモ\n"
    profile_path.write_text(edited, encoding="utf-8")
    simulation.export_profiles(path=profile_path, experiment_id="conversation_003")
    assert profile_path.read_text(encoding="utf-8") == edited


def test_partner_and_unselected_candidates_do_not_increment_app_counter():
    state = simulation.new_state()
    assert simulation.can_send_app(state)
    state["turns"].append({"candidates": [{"text": "未送信候補"}], "selected_text": None})
    simulation.send_partner_message(state, "架空の相手からの返事")
    assert state["app_sent_count"] == 0


def test_rejecting_unsafe_pending_candidates_persists_them_without_sending(tmp_path):
    state = state_with_sent(15)
    state["api_requests"] = [{"request_number": index, "ok": True} for index in range(1, 17)]
    state["pending_generation"] = {
        "account": "API1", "model": "gemini-3.5-flash-lite",
        "data": {"conversation_stage": "Stage 2", "invite_decision": "continue_conversation"},
        "candidates": [
            {"label": "A", "text": "すぐ買うことが多いです！"},
            {"label": "B", "text": "お店の前で立ち止まります！"},
            {"label": "C", "text": '<script>alert("x")</script>'},
        ],
    }
    reason = "本人未確認の購買行動を3案が断定したため送信を停止"

    simulation.reject_pending_generation(state, reason)

    assert state["status"] == "BLOCKED"
    assert state["end_reason"] == reason
    assert "pending_generation" not in state
    assert state["app_sent_count"] == 15
    assert len(state["messages"]) == 0
    assert state["rejected_generations"][0]["candidates"][2]["text"].startswith("<script>")
    target = tmp_path / "blocked.html"
    simulation.render_html(state, target)
    report = target.read_text(encoding="utf-8")
    assert "送信前に拒否したGemini候補を確認" in report
    assert "本人未確認の購買行動" in report
    assert "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in report
    assert '<script>alert("x")</script>' not in report


def test_reject_pending_generation_requires_running_pending_state():
    state = state_with_sent(0)
    with pytest.raises(ValueError, match="拒否できる未送信候補がありません"):
        simulation.reject_pending_generation(state, "安全上の理由")


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


def test_api_selection_metadata_is_returned_by_backend_without_harness_rotation():
    assert not hasattr(simulation, "MODEL_ORDER")
    assert not hasattr(simulation, "fallback_slot")
    assert "GEMINI_API_KEY" not in __import__("inspect").getsource(simulation.main_run)
    assert "GEMINI_MODEL" not in __import__("inspect").getsource(simulation.main_run)
    record = simulation.api_request_record(
        {
            "api_alias": "API2", "model": "gemini-3.5-flash-lite", "api_attempt_count": 3,
            "attempted_models": [
                {"api_alias": "API1", "model": "gemini-3.5-flash-lite"},
                {"api_alias": "API2", "model": "gemini-3.5-flash-lite"},
            ],
        }, 1, 200
    )
    assert (record["api_alias"], record["model"], record["attempt_count"]) == (
        "API2", "gemini-3.5-flash-lite", 3
    )
    assert record["attempted_models"] == [
        {"api_alias": "API1", "model": "gemini-3.5-flash-lite"},
        {"api_alias": "API2", "model": "gemini-3.5-flash-lite"},
    ]


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


def test_twentieth_send_waits_for_partner_final_reply():
    state = state_with_sent(19)
    turn = {}
    simulation.send_app_message(state, "20通目です", turn)
    assert state["status"] == "RUNNING"
    assert simulation.can_receive_partner(state)
    simulation.send_partner_message(state, "楽しかったです！")
    simulation.finalize_after_partner_reply(state)
    assert state["status"] == "LIMIT_REACHED"
    assert state["partner_sent_count"] == 1
    assert not simulation.can_send_app(state)


def test_partner_refusal_is_saved_before_safety_stop():
    state = state_with_sent(2)
    simulation.send_partner_message(state, "ごめんなさい！これ以上やり取りするのは控えたいです")
    simulation.finalize_after_partner_reply(state)
    assert state["messages"][-1]["body"].startswith("ごめんなさい")
    assert state["status"] == "SAFETY_STOP"


def test_apology_for_a_late_reply_is_not_a_safety_refusal():
    assert not simulation.is_partner_refusal("ごめんなさい、返信遅くなりました！")


@pytest.mark.parametrize("message", [
    "これ以上のやり取りは控えさせてください",
    "今後は連絡を控えさせていただきます",
    "今後はメッセージを控えさせてください",
    "もうやり取りしません",
])
def test_polite_contact_refusal_variants_are_safety_stops(message):
    assert simulation.is_partner_refusal(message)


def test_confirm_success_cannot_override_safety_stop_or_latest_refusal():
    state = state_with_sent(3)
    state["messages"] = [
        {"speaker": "app", "body": "土曜日18時に横浜駅のカフェで会いませんか？"},
        {"speaker": "partner", "body": "いいですね！"},
        {"speaker": "partner", "body": "ごめんなさい！これ以上やり取りするのは控えたいです"},
    ]
    state["pending_meeting_confirmation"] = {"proposal": state["messages"][0]["body"], "acceptance": state["messages"][1]["body"]}
    simulation.finalize_after_partner_reply(state)
    assert state["status"] == "SAFETY_STOP"
    with pytest.raises(ValueError, match="安全停止"):
        simulation.confirm_meeting_success(state)
    assert state["status"] == "SAFETY_STOP"


def test_meeting_agreement_can_be_built_across_saved_turns():
    messages = [
        {"speaker": "app", "body": "よかったらカフェに行きませんか？"},
        {"speaker": "partner", "body": "いいですね！"},
        {"speaker": "app", "body": "土曜日はどうですか？"},
        {"speaker": "partner", "body": "大丈夫です！"},
        {"speaker": "app", "body": "では18時ごろに横浜駅近くでどうでしょう"},
        {"speaker": "partner", "body": "大丈夫です！楽しみにしてます"},
    ]
    assert simulation.find_meeting_agreement(messages)
    state = state_with_sent(3)
    state["messages"] = messages
    simulation.prepare_meeting_confirmation(state)
    simulation.confirm_meeting_success(state)
    assert state["status"] == "SUCCESS"
    assert "土曜日" in state["meeting_agreement"]["proposal"]
    assert "横浜駅" in state["meeting_agreement"]["proposal"]


def test_meeting_requires_concrete_mutual_agreement():
    assert not simulation.find_meeting_agreement([
        {"speaker": "app", "body": "今度カフェ行きませんか？"},
        {"speaker": "partner", "body": "いつか行きたいですね！"},
    ])
    assert not simulation.find_meeting_agreement([
        {"speaker": "app", "body": "土曜日18時に横浜駅でどうですか？"},
        {"speaker": "partner", "body": "ごめんなさい、難しいです"},
    ])


def test_json_restore_recreates_fictional_data_only_in_empty_database(tmp_path, monkeypatch):
    state = simulation.new_state()
    state["match_id"] = 1
    state["people"]["app_user"]["profile"] = "架空本人プロフィール"
    state["messages"] = [
        {"sequence": 1, "speaker": "partner", "body": "架空の開始メッセージ"},
        {"sequence": 2, "speaker": "app", "body": "未送信候補ではない送信済み文", "app_send_number": 1},
    ]
    state["turns"] = [{"turn_number": 1, "selected_text": "未送信候補ではない送信済み文", "candidates": [{"text": "代替候補"}]}]
    state["app_sent_count"] = 1
    state["partner_sent_count"] = 1
    state["api_requests"] = [{"request_number": 1, "ok": True, "model": "fictional-model", "api_alias": "API1", "attempt_count": 2}]
    state["pending_generation"] = {
        "account": "API1", "model": "fictional-model", "data": {"demo": False},
        "candidates": [{"label": "推奨", "text": "未送信候補"}], "settings": {"count": 3},
    }
    json_path = tmp_path / "resume.json"
    json_path.write_text(__import__("json").dumps(state, ensure_ascii=False), encoding="utf-8")
    data_dir = tmp_path / "empty-db"
    client = simulation.import_app(data_dir)
    restored = simulation.restore_state_to_empty_db(client, state)
    assert restored["match_id"] == 1
    assert simulation.db_matches_state(client, restored)
    assert client.get("/api/profile").json()["content"] == "架空本人プロフィール"
    assert restored["pending_generation"] == state["pending_generation"]
    assert len(restored["api_requests"]) == 1

    nonempty = tmp_path / "nonempty-db"
    other = simulation.import_app(nonempty)
    other.post("/api/matches", json={"name": "Existing", "description": "keep"})
    with pytest.raises(RuntimeError, match="空の実験用SQLite"):
        simulation.restore_state_to_empty_db(other, state)


def test_restore_validates_entire_json_before_mutating_database(tmp_path):
    state = simulation.new_state()
    state["messages"] = [
        {"sequence": 1, "speaker": "partner", "body": "valid first message"},
        {"sequence": 2, "speaker": "other", "body": "invalid later message"},
    ]
    state["partner_sent_count"] = 1
    client = simulation.import_app(tmp_path / "prevalidate")
    with pytest.raises(ValueError, match="JSON"):
        simulation.restore_state_to_empty_db(client, state)
    assert client.get("/api/profile").json()["content"] == ""
    assert client.get("/api/matches").json() == []


def test_restore_rolls_back_all_rows_when_sqlite_insert_fails(tmp_path):
    import sqlite3
    import sys

    state = simulation.new_state()
    state["messages"] = [
        {"sequence": 1, "speaker": "partner", "body": "valid first message"},
        {"sequence": 2, "speaker": "app", "body": "BOOM", "app_send_number": 1},
    ]
    state["app_sent_count"] = 1
    state["partner_sent_count"] = 1
    state["turns"] = [{"candidates": [{"text": "saved text"}]}]
    client = simulation.import_app(tmp_path / "rollback")
    backend = sys.modules["app"]
    client.get("/api/profile")
    with sqlite3.connect(backend.DB) as connection:
        connection.execute("CREATE TRIGGER reject_restore_message BEFORE INSERT ON messages WHEN NEW.body='BOOM' BEGIN SELECT RAISE(ABORT, 'fixture'); END")
    with pytest.raises(RuntimeError, match="トランザクション"):
        simulation.restore_state_to_empty_db(client, state)
    assert client.get("/api/profile").json()["content"] == ""
    assert client.get("/api/matches").json() == []


def test_restore_rolls_back_when_transaction_integrity_check_detects_mutated_message(tmp_path):
    import sqlite3
    import sys

    state = simulation.new_state()
    state["messages"] = [{"sequence": 1, "speaker": "partner", "body": "original"}]
    state["partner_sent_count"] = 1
    client = simulation.import_app(tmp_path / "integrity-rollback")
    backend = sys.modules["app"]
    client.get("/api/profile")
    with sqlite3.connect(backend.DB) as connection:
        connection.execute(
            "CREATE TRIGGER mutate_restored_message AFTER INSERT ON messages "
            "WHEN NEW.body='original' BEGIN UPDATE messages SET body='mutated' WHERE id=NEW.id; END"
        )
    with pytest.raises(RuntimeError, match="トランザクション内の整合性"):
        simulation.restore_state_to_empty_db(client, state)
    assert client.get("/api/profile").json()["content"] == ""
    assert client.get("/api/matches").json() == []


def test_generation_metadata_is_from_single_backend_response():
    assert simulation.api_request_record(
        {"api_alias": "API2", "model": "gemini-3.5-flash-lite", "api_attempt_count": 3},
        request_number=1, http_status=200,
    ) == {
        "request_number": 1, "ok": True, "api_alias": "API2",
        "model": "gemini-3.5-flash-lite", "attempt_count": 3,
        "attempted_models": [], "error_code": None, "app_http_status": 200,
    }
    failed = simulation.api_request_record({"detail": "レート制限"}, request_number=2, http_status=502)
    assert failed["attempt_count"] is None


def test_rate_limit_failure_metadata_is_persisted_without_secrets(tmp_path):
    result = {
        "detail": "Geminiの無料利用枠またはレート制限に達しました。",
        "api_attempt_count": 4,
        "attempted_models": [
            {"api_alias": "API1", "model": "gemini-3.5-flash-lite"},
            {"api_alias": "API2", "model": "gemini-3.5-flash-lite"},
            {"api_alias": "API1", "model": "gemini-3.1-flash-lite"},
            {"api_alias": "API2", "model": "gemini-3.1-flash-lite"},
        ],
    }
    request = simulation.api_request_record(result, request_number=1, http_status=502)
    state = simulation.new_state()
    state["api_requests"].append(request)
    path = tmp_path / "blocked.json"
    simulation.save_state(state, path)
    saved = __import__("json").loads(path.read_text(encoding="utf-8"))["api_requests"][0]
    assert saved["attempt_count"] == 4
    assert saved["attempted_models"] == result["attempted_models"]
    assert saved["detail"] == result["detail"]
    assert "AIza" not in __import__("json").dumps(saved)


@pytest.mark.parametrize("failure", ["transport", "invalid_json"])
def test_generation_transport_or_json_failure_is_saved_and_not_automatically_retried(tmp_path, failure):
    class FakeResponse:
        status_code = 200

        def json(self):
            raise ValueError("private raw body should not be saved")

    class FakeClient:
        calls = 0

        def post(self, *args, **kwargs):
            self.calls += 1
            if failure == "transport":
                raise TimeoutError("private network payload")
            return FakeResponse()

    state = simulation.new_state()
    client = FakeClient()
    json_path, html_path = tmp_path / "blocked.json", tmp_path / "blocked.html"
    assert simulation.call_generate_once(client, {}, state, json_path, html_path) is None
    assert client.calls == 1
    assert state["status"] == "BLOCKED"
    assert state["generation_uncertain"] is True
    assert len(state["api_requests"]) == 1
    assert state["api_requests"][0]["ok"] is False
    assert state["api_requests"][0]["app_http_status"] == (0 if failure == "transport" else 200)
    saved_json = json_path.read_text(encoding="utf-8")
    assert "private raw body" not in saved_json
    assert "private network payload" not in saved_json
    assert html_path.is_file()
    assert not simulation.allow_uncertain_generation_retry(state)


def test_needs_user_info_pauses_without_candidates_or_send_then_accepts_answers():
    state = simulation.new_state()
    state["match_id"] = 12
    data = {
        "needs_user_info": True,
        "user_questions": [{"question": "どんな映画が好きですか？", "purpose": "本人の好みを確認するため"}],
        "user_info_reason": "本人の映画の好みが不明です。",
        "recommended": None,
        "alternatives": [],
    }
    settings = simulation.generation_settings(12, "自然に会話を広げる", "")
    simulation.pause_for_user_info(state, data, settings, request_number=1)
    assert state["status"] == "AWAITING_USER_INFO"
    assert state["app_sent_count"] == 0
    assert simulation.resume_user_info_settings(state, [], skip=False) is None
    answered = simulation.resume_user_info_settings(state, ["洋画が好きです"], skip=False)
    assert answered["user_answers"] == [{"question": "どんな映画が好きですか？", "answer": "洋画が好きです"}]
    assert answered["response_version"] == 2
    assert state["status"] == "RUNNING"
    assert not state["app_sent_count"]
    assert "洋画が好き" not in state["people"]["app_user"]["profile"]


def test_resume_awaiting_user_info_does_not_regenerate_until_answered(tmp_path, monkeypatch):
    class JsonResponse:
        status_code = 200

        def json(self):
            return {
                "demo": False, "api_alias": "API1", "model": "gemini-3.5-flash-lite",
                "api_attempt_count": 1,
                "recommended": {"label": "推奨", "text": "映画好きです！"},
                "alternatives": [
                    {"label": "別案1", "text": "映画はよく観ます！"},
                    {"label": "別案2", "text": "洋画が好きなんですね！"},
                ],
                "reason": "回答を反映", "strategy": "会話を続ける",
            }

    data_dir = tmp_path / "resume-data"
    seeded = simulation.import_app(data_dir)
    seeded.put("/api/profile", json={"content": "架空プロフィール", "avoid": ""})
    created = seeded.post("/api/matches", json={"name": "架空の相手", "description": "映画が好き"})
    match_id = created.json()["id"]
    seeded.post(f"/api/matches/{match_id}/messages", json={"role": "them", "body": "映画好きですか？"})

    state = simulation.new_state()
    state["status"] = "AWAITING_USER_INFO"
    state["match_id"] = match_id
    state["messages"] = [{"sequence": 1, "speaker": "partner", "body": "映画好きですか？"}]
    state["partner_sent_count"] = 1
    state["api_requests"] = [{"request_number": 1, "ok": True, "result_type": "needs_user_info", "attempt_count": 0, "attempted_models": []}]
    simulation.pause_for_user_info(state, {
        "needs_user_info": True,
        "user_questions": [{"question": "映画は好きですか？", "purpose": "本人情報の確認"}],
        "user_info_reason": "本人の好みを確認するため",
        "recommended": None, "alternatives": [],
    }, simulation.generation_settings(match_id, "自然に会話を広げる", ""), 1)
    json_path, html_path, profile_path = tmp_path / "state.json", tmp_path / "state.html", tmp_path / "profiles.md"
    simulation.save_state(state, json_path)
    monkeypatch.setattr(simulation, "JSON_FILE", json_path)
    monkeypatch.setattr(simulation, "HTML_FILE", html_path)
    monkeypatch.setattr(simulation, "PROFILE_FILE", profile_path)
    monkeypatch.setattr(simulation, "DATA_DIR", data_dir)

    class CountingClient:
        generate_calls = 0

        def get(self, path):
            return seeded.get(path)

        def post(self, path, **kwargs):
            if path == "/api/generate":
                self.generate_calls += 1
                self.last_settings = kwargs["json"]
                return JsonResponse()
            return seeded.post(path, **kwargs)

        def put(self, path, **kwargs):
            return seeded.put(path, **kwargs)

    client = CountingClient()
    monkeypatch.setattr(simulation, "import_app", lambda _path: client)
    assert simulation.main_run(None, True, None, None, "自然に会話を広げる", "", False) == 0
    assert client.generate_calls == 0
    assert __import__("json").loads(json_path.read_text(encoding="utf-8"))["status"] == "AWAITING_USER_INFO"

    assert simulation.main_run(None, True, None, None, "自然に会話を広げる", "", False, ["洋画が好きです"]) == 0
    assert client.generate_calls == 1
    assert client.last_settings["user_answers"] == [{"question": "映画は好きですか？", "answer": "洋画が好きです"}]
    resumed = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert resumed["app_sent_count"] == 0
    assert resumed["pending_generation"]["settings"]["user_answers"] == client.last_settings["user_answers"]


def test_simulation_requests_backend_metadata_response_version_two():
    assert simulation.generation_settings(23, "自然に会話を広げる", "") == {
        "mode": "reply", "match_id": 23, "count": 3, "tone": "自動",
        "direction": "自然に会話を広げる", "extra": "", "show_policy": True,
        "response_version": 2,
    }


def test_start_bat_starts_and_waits_before_opening_firefox():
    script = (ROOT / "start.bat").read_text(encoding="utf-8")
    runner = (ROOT / "scripts" / "start_server.py").read_text(encoding="utf-8")
    assert "taskkill" not in script.lower()
    assert "Firefox" in script
    assert "MRA_PORT" in script
    assert "start_server.py" in script
    assert "uvicorn.Config" in runner
    assert runner.index("if server.started and local_app_ready(port)") < runner.index("print(f\"Ready at {url}") < runner.rindex("subprocess.Popen([firefox, url])")
    assert "/api/status" in runner
    assert "matching-reply-assistant" in runner
    assert "/api/profile" not in script
    assert "Start-Process" not in script
    assert "Ctrl+C" in script
