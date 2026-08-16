"""
Tests for backend/services/assistant_service.py's generate_content_with_retry -
the shared wrapper used by both the AI assistant and the financial health
coach chat to call Gemini.

These specifically guard against a real production issue: the app was
originally pinned to "gemini-flash-latest", which Google documents as an
EXPERIMENTAL alias with tighter rate limits than a stable model - the
direct cause of users hitting frequent 503 UNAVAILABLE "high demand"
errors. Fixed by (1) switching to a real, stable model name, and (2) adding
retry-with-backoff so an occasional transient 503/429 - which can still
happen against any external API under real load, even a stable model -
doesn't immediately surface as a failure to the user.
"""
import os
import sys
import time
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services import assistant_service
from google.genai import errors as genai_errors


def _server_error(code=503):
    return genai_errors.ServerError(code, {"error": {"message": "overloaded", "code": code}})


def _client_error(code=400):
    return genai_errors.ClientError(code, {"error": {"message": "bad request", "code": code}})


class TestGenerateContentWithRetry:
    def test_succeeds_immediately_when_no_error(self):
        mock_response = MagicMock()
        mock_response.text = "hello"
        with patch.object(assistant_service._client.models, "generate_content", return_value=mock_response) as m:
            result = assistant_service.generate_content_with_retry("gemini-3.6-flash", "prompt")
        assert result.text == "hello"
        assert m.call_count == 1

    def test_retries_on_server_error_and_eventually_succeeds(self):
        mock_response = MagicMock()
        mock_response.text = "succeeded on retry"
        side_effects = [_server_error(503), _server_error(503), mock_response]

        with patch.object(assistant_service._client.models, "generate_content", side_effect=side_effects) as m:
            with patch("time.sleep"):  # don't actually wait during tests
                result = assistant_service.generate_content_with_retry("gemini-3.6-flash", "prompt", max_retries=2)

        assert result.text == "succeeded on retry"
        assert m.call_count == 3

    def test_raises_server_error_after_exhausting_retries(self):
        with patch.object(
            assistant_service._client.models, "generate_content", side_effect=_server_error(503)
        ) as m:
            with patch("time.sleep"):
                with pytest.raises(genai_errors.ServerError):
                    assistant_service.generate_content_with_retry("gemini-3.6-flash", "prompt", max_retries=2)

        assert m.call_count == 3  # initial attempt + 2 retries

    def test_client_error_is_not_retried(self):
        """
        A 4xx (bad request, auth failure, etc.) will never succeed on
        retry - regression test to make sure only ServerError (5xx)
        triggers the retry loop, not every exception.
        """
        with patch.object(
            assistant_service._client.models, "generate_content", side_effect=_client_error(400)
        ) as m:
            with pytest.raises(genai_errors.ClientError):
                assistant_service.generate_content_with_retry("gemini-3.6-flash", "prompt", max_retries=2)

        assert m.call_count == 1  # no retries at all

    def test_backoff_increases_between_retries(self):
        """Locks in the 1s, 2s, 4s... exponential pattern, not just that sleep gets called."""
        sleep_calls = []

        def fake_sleep(seconds):
            sleep_calls.append(seconds)

        mock_response = MagicMock()
        mock_response.text = "ok"
        side_effects = [_server_error(503), _server_error(503), mock_response]

        with patch.object(assistant_service._client.models, "generate_content", side_effect=side_effects):
            with patch("time.sleep", side_effect=fake_sleep):
                assistant_service.generate_content_with_retry("gemini-3.6-flash", "prompt", max_retries=2)

        assert sleep_calls == [1, 2]


class TestGeminiModelIsStable:
    def test_model_name_is_not_the_experimental_latest_alias(self):
        """
        Regression test for the actual root cause: "gemini-flash-latest"
        is documented by Google as experimental with tighter rate limits.
        This just checks the model name doesn't end in "-latest" - a
        stand-in for "don't silently revert to the experimental alias".
        """
        assert not assistant_service._GEMINI_MODEL.endswith("-latest")

    def test_financial_health_service_uses_the_same_model_constant(self):
        from backend.services import financial_health_service
        assert financial_health_service._GEMINI_MODEL == assistant_service._GEMINI_MODEL
