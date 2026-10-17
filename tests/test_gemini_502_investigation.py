"""Investigate exact exception types that trigger 502 gemini_connection_error with attempt_count=0."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(r"C:\Users\poiuy\desktop\aichatapp2\verification-repo")
sys.path.insert(0, str(REPO))

import app
from fastapi.testclient import TestClient


class Test502Investigation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app.app)
        # Create a fresh match
        res = self.client.post("/api/matches", json={"name": "調査相手", "description": "調査用相手役"})
        self.match_id = res.json()["id"]

    def test_when_client_constructor_raises_then_502_with_zero_attempts(self):
        """If genai.Client raises in constructor, generate returns 502 with attempt_count=0."""
        with patch("google.genai.Client", side_effect=Exception("Client init failed")):
            res = self.client.post("/api/generate", json={
                "mode": "first", "match_id": self.match_id, "response_version": 2, "count": 3,
                "tone": "自動", "direction": "自然に会話を広げる", "show_policy": True
            })
            self.assertEqual(res.status_code, 502)
            body = res.json()
            self.assertEqual(body["error_code"], "gemini_connection_error")
            self.assertEqual(body["api_attempt_count"], 0)
            print("\n[Case A] Client constructor exception -> 502, api_attempt_count=0 confirmed")

    def test_when_timeout_is_zero_or_negative(self):
        """Test how genai.Client handles timeout=0 or negative."""
        from google.genai import types
        # Does types.HttpOptions accept negative timeout?
        try:
            opt = types.HttpOptions(timeout=-1)
            print("\n[Case B] HttpOptions(timeout=-1):", opt)
        except Exception as e:
            print("\n[Case B] HttpOptions(timeout=-1) raised:", type(e), e)

    def test_when_configurations_exhausted_with_unknown_error(self):
        """When generate_content raises an unexpected non-rate-limit exception before append?
        Wait! In app.py:
        attempted_models.append({'api_alias': account, 'model': model}) is line 8157,
        and client.models.generate_content(...) is line 8158!
        If generate_content raises, attempted_models has length >= 1!
        So attempt_count CANNOT be 0 if generate_content was called!"""
        pass


if __name__ == "__main__":
    unittest.main()
