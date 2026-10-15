"""Run the real FastAPI app while replacing only the Gemini SDK client.

This helper is copied into a temporary app directory by the Firefox integration
test. It never instantiates the real SDK client and therefore cannot contact
Gemini or any other external provider.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from google import genai


class DeterministicModels:
    def generate_content(self, *, model, contents, config):
        request_context = json.loads(contents)
        mode = request_context.get("mode", "unknown")
        ephemeral_answers = request_context.get("ephemeral_user_answers", [])
        expected_movie_answer = "映画は好きで洋画をよく観ます"
        user_answer_matches_expected = any(
            answer.get("answer", "") == expected_movie_answer
            for answer in ephemeral_answers
        )
        call_log = Path(os.environ["MRA_TEST_GEMINI_CALL_LOG"])
        call_log.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": model,
            "mode": mode,
            "user_answer_count": len(ephemeral_answers),
            "user_answer_matches_expected": user_answer_matches_expected,
            "input_contains_incoming_message": "休日は友達とカフェに行ってきました！" in contents,
            "system_instruction_present": bool(getattr(config, "system_instruction", None)),
        }
        with call_log.open("a", encoding="utf-8") as log:
            log.write(json.dumps(payload, ensure_ascii=False) + "\n")

        candidates_by_mode = {
            "first": {
                "recommended": {
                    "label": "自然な初回メッセージ",
                    "text": "はじめまして！\nプロフィールの雰囲気が気になっていました\nマッチできてうれしいです☺️\nカフェ巡り好きなんですね！\n最近行ったお店ありますか？",
                    "reply_move": "react",
                },
                "alternatives": [
                    {
                        "label": "読書の話題",
                        "text": "マッチありがとうございます！\nお話ししてみたいなと思っていたのでうれしいです\n読書がお好きなんですね！\nどんな本を読むことが多いですか？",
                        "reply_move": "expand",
                    },
                    {
                        "label": "旅行の話題",
                        "text": "はじめまして！\nマッチできてうれしいです✨\n旅行がお好きなんですね！最近行ってみたい場所はありますか？",
                        "reply_move": "grounded_share",
                    },
                ],
            },
            "followup": {
                "recommended": {
                    "label": "控えめな追いメッセージ",
                    "text": "こんにちは！\nまたお話しできたらうれしいです\n返信は気にしないでくださいね",
                    "reply_move": "react",
                },
                "alternatives": [
                    {
                        "label": "短く待つ",
                        "text": "また時間があるときにお話しできたらうれしいです",
                        "reply_move": "expand",
                    },
                    {
                        "label": "別の控えめな表現",
                        "text": "最近少しずつ涼しくなってきましたね！\n無理のないときにまたお話しできたらうれしいです",
                        "reply_move": "grounded_share",
                    },
                ],
            },
            "like": {
                "recommended": {
                    "label": "プロフィールの話題",
                    "text": "プロフィールのカフェ巡りが気になりました！\n最近行ってよかったお店はありますか？",
                    "reply_move": "react",
                },
                "alternatives": [
                    {
                        "label": "旅行の話題",
                        "text": "旅行がお好きなんですね！\n最近気になっている行き先はありますか？",
                        "reply_move": "expand",
                    },
                    {
                        "label": "短いきっかけ",
                        "text": "美術館に行くの楽しそうですね！\n最近印象に残った展示はありますか？",
                        "reply_move": "grounded_share",
                    },
                ],
            },
            "reply": {
                "recommended": {
                    "label": "自然な反応",
                    "text": "えーいいですね！\nどんなカフェだったんですか？",
                    "reply_move": "react",
                },
                "alternatives": [
                    {
                        "label": "話題を広げる",
                        "text": "カフェ巡りってお店ごとに雰囲気が違いそうですね！\n最近行った中で印象に残ったお店ありますか？",
                        "reply_move": "expand",
                    },
                    {
                        "label": "別の切り口",
                        "text": "お店選びって写真や口コミを見て決めることが多いですか？",
                        "reply_move": "grounded_share",
                    },
                ],
            },
        }
        mode_candidates = candidates_by_mode.get(mode, candidates_by_mode["reply"])
        if (
            mode == "reply"
            and os.environ.get("MRA_TEST_REQUIRE_MOVIE_ANSWER") == "1"
            and user_answer_matches_expected
        ):
            mode_candidates = {
                "recommended": {
                    "label": "確認回答を使った返信",
                    "text": "映画好きで洋画をよく観ます！",
                    "reply_move": "react",
                },
                "alternatives": [
                    {
                        "label": "短い回答",
                        "text": "映画は好きです！",
                        "reply_move": "grounded_share",
                    },
                    {
                        "label": "回答の補足",
                        "text": "洋画を見ることが多いです！",
                        "reply_move": "expand",
                    },
                ],
            }
        response = {
            "needs_user_info": False,
            "user_questions": [],
            "user_info_reason": "",
            **mode_candidates,
            "reason": "相手が話したカフェの話題を受けて具体的に尋ねます",
            "strategy": "まずカフェの雰囲気を聞いて会話を続けます",
            "conversation_stage": "Stage 1" if mode == "first" else "Stage 2",
            "invite_decision": "do_not_invite" if mode == "first" else "continue_conversation",
            "decision_reason": "会話を始めた段階なので相手の好みをもう少し聞きます",
            "next_action": "相手が話したカフェの内容を受け止めます",
        }

        class Response:
            text = json.dumps(response, ensure_ascii=False)

        return Response()


class DeterministicClient:
    def __init__(self, *, api_key, http_options):
        # Deliberately do not retain, inspect, or log the placeholder key.
        self.models = DeterministicModels()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    if args.host != "127.0.0.1":
        raise SystemExit("The Firefox integration server must bind to loopback only")

    genai.Client = DeterministicClient

    import uvicorn

    uvicorn.run("app:app", host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
