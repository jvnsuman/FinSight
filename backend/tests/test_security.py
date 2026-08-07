"""
Unit tests for backend/core/security.py - password hashing, JWT issuing/
verification, and device-info parsing. No database needed; these are all
pure functions.
"""
import os
import sys
from datetime import timedelta

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.core import security


class TestPasswordHashing:
    def test_hash_password_returns_different_string_than_input(self):
        hashed = security.hash_password("correct-horse-battery-staple")
        assert hashed != "correct-horse-battery-staple"

    def test_verify_password_succeeds_for_correct_password(self):
        hashed = security.hash_password("correct-horse-battery-staple")
        assert security.verify_password("correct-horse-battery-staple", hashed) is True

    def test_verify_password_fails_for_wrong_password(self):
        hashed = security.hash_password("correct-horse-battery-staple")
        assert security.verify_password("wrong-password", hashed) is False

    def test_same_password_hashed_twice_produces_different_hashes(self):
        # bcrypt salts automatically - two hashes of the same password must
        # never be identical, or salting isn't actually happening.
        first = security.hash_password("same-password")
        second = security.hash_password("same-password")
        assert first != second
        # but both must still verify correctly
        assert security.verify_password("same-password", first) is True
        assert security.verify_password("same-password", second) is True


class TestAccessTokens:
    def test_create_and_decode_round_trip(self):
        token = security.create_access_token({"sub": "42"})
        payload = security.decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "42"

    def test_decode_rejects_garbage_token(self):
        assert security.decode_access_token("not.a.real.jwt") is None

    def test_decode_rejects_expired_token(self):
        token = security.create_access_token(
            {"sub": "42"}, expires_delta=timedelta(seconds=-1)
        )
        assert security.decode_access_token(token) is None

    def test_token_carries_custom_claims(self):
        # e.g. the "sid" session claim used by session management
        token = security.create_access_token({"sub": "1", "sid": "session-abc"})
        payload = security.decode_access_token(token)
        assert payload["sid"] == "session-abc"


class TestVerificationTokens:
    def test_generate_verification_token_is_url_safe_and_nonempty(self):
        token = security.generate_verification_token()
        assert len(token) > 0
        # url_safe tokens should not contain characters that need URL-encoding
        assert " " not in token
        assert "/" not in token

    def test_generate_verification_token_is_unique_each_call(self):
        tokens = {security.generate_verification_token() for _ in range(50)}
        assert len(tokens) == 50


class TestDeviceInfoParsing:
    def test_parse_device_info_detects_chrome_on_windows(self):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        label = security.parse_device_info(ua)
        assert "Chrome" in label
        assert "Windows" in label

    def test_parse_device_info_detects_safari_on_mac(self):
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15"
        label = security.parse_device_info(ua)
        assert "Safari" in label
        assert "macOS" in label

    def test_parse_device_info_detects_edge(self):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36 Edg/120.0"
        label = security.parse_device_info(ua)
        assert "Edge" in label

    def test_parse_device_info_ios_user_agent_currently_labeled_as_macos(self):
        """
        NOTE - this documents a real quirk in parse_device_info, not desired
        behavior: a genuine iPhone Safari UA contains both "like Mac OS X"
        and "iPhone", and since the "mac os"/"macintosh" check runs before
        the "iphone"/"ipad" check, every iOS device is currently labeled
        macOS instead of iOS. This test locks in that CURRENT behavior so a
        future fix to the check order is a deliberate, visible change here
        rather than a silent regression - the fix would be reordering the
        iOS check before the macOS check.
        """
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
        label = security.parse_device_info(ua)
        assert "macOS" in label  # currently mislabeled; see docstring above

    def test_parse_device_info_handles_none_gracefully(self):
        # Should not raise even when no User-Agent header was sent
        assert security.parse_device_info(None) == "Unknown device"

    def test_parse_device_info_handles_empty_string(self):
        assert security.parse_device_info("") == "Unknown device"

    def test_parse_device_info_handles_unrecognized_agent(self):
        label = security.parse_device_info("SomeWeirdBot/1.0")
        assert isinstance(label, str)
        assert len(label) > 0
