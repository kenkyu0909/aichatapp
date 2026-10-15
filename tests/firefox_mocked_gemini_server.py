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
        call_log = Path(os.environ["MRA_TEST_GEMINI_CALL_LOG"])
        call_log.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": model,
            "input_contains_incoming_message": "休日は友達とカフェに行ってきました！" in contents,
            "system_instruction_present": bool(getattr(config, "system_instruction", None)),
        }
        with call_log.open("a", encoding="utf-8") as log:
            log.write(json.dumps(payload, ensure_ascii=False) + "\n")

        response = {
            "needs_user_info": False,
            "user_questions": [],
            "user_info_reason": "",
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
            "reason": "相手が話したカフェの話題を受けて具体的に尋ねます",
            "strategy": "まずカフェの雰囲気を聞いて会話を続けます",
            "conversation_stage": "Stage 2",
            "invite_decision": "continue_conversation",
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
