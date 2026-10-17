"""Tests for run20.py circuit breaker and failure caps."""
import argparse
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(r"C:\Users\poiuy\desktop\aichatapp2\verification-repo")
CONV_DIR = Path(r"C:\Users\poiuy\desktop\aichatapp2\会話テスト")
sys.path.insert(0, str(CONV_DIR))
sys.path.insert(0, str(REPO))

import run20


class TestRun20CircuitBreaker(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "test_state.json"
        self.html_file = Path(self.temp_dir.name) / "test_html.html"
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        os.environ["CONV_STATE"] = str(self.state_file)
        os.environ["CONV_HTML"] = str(self.html_file)
        os.environ["CONV_DATA"] = str(self.data_dir)

        # Patch run20 paths
        run20.STATE = self.state_file
        run20.HTML = self.html_file
        run20.DATA = self.data_dir

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_circuit_breaker_stops_on_three_consecutive_502_in_same_turn(self):
        """When generate endpoint returns 502 three times in one turn, cmd_turn exits with SystemExit."""
        state = run20.new_state()
        state["match_id"] = 1
        state["app_sent_count"] = 1
        state["messages"] = [
            {"speaker": "app", "body": "はじめまして", "at": "2026-10-17T00:00:00Z"},
            {"speaker": "partner", "body": "よろしく", "at": "2026-10-17T00:01:00Z"},
        ]
        state["partner_sent_count"] = 1
        run20.save(state)

        mock_res = MagicMock()
        mock_res.status_code = 502
        mock_res.json.return_value = {
            "error_code": "gemini_connection_error",
            "detail": "Geminiとの通信に失敗しました",
            "api_attempt_count": 0,
        }

        with patch("fastapi.testclient.TestClient.post", return_value=mock_res):
            args = argparse.Namespace(
                first=False, partner="", append_partner="", select=1,
                direction="自然に会話を広げる", answer=[], drop_pending=False, attempts=3
            )
            with self.assertRaises(SystemExit) as ctx:
                run20.cmd_turn(args)
            self.assertIn("同一ターンで接続エラーが連続3回", str(ctx.exception))

        saved = run20.load()
        self.assertEqual(saved["status"], "BLOCKED")
        self.assertIn("同一ターンでの連続接続エラー(3回)", saved["end_reason"])

    def test_circuit_breaker_stops_on_ten_cumulative_502_errors(self):
        """When cumulative 502 errors reach 10, cmd_turn exits with SystemExit before generating."""
        state = run20.new_state()
        state["match_id"] = 1
        state["app_sent_count"] = 1
        state["messages"] = [
            {"speaker": "app", "body": "はじめまして", "at": "2026-10-17T00:00:00Z"},
            {"speaker": "partner", "body": "よろしく", "at": "2026-10-17T00:01:00Z"},
        ]
        state["partner_sent_count"] = 1
        # Populate 10 prior 502 requests
        state["requests"] = [{"http_status": 502} for _ in range(10)]
        run20.save(state)

        args = argparse.Namespace(
            first=False, partner="", append_partner="", select=1,
            direction="自然に会話を広げる", answer=[], drop_pending=False, attempts=3
        )
        with self.assertRaises(SystemExit) as ctx:
            run20.cmd_turn(args)
        self.assertIn("テスト全体の接続エラーが累計10回", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
