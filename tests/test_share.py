"""Tests for env_vault.share — secure shareable tokens."""

import time
import pytest
from pathlib import Path

from env_vault.share import (
    create_share_token,
    decode_share_token,
    save_share_token,
    load_share_token,
)

PASS = "hunter2"


def test_create_returns_string():
    token = create_share_token("DB_URL", "postgres://localhost/db", PASS)
    assert isinstance(token, str)
    assert len(token) > 0


def test_roundtrip_key_and_value():
    token = create_share_token("API_KEY", "secret123", PASS)
    result = decode_share_token(token, PASS)
    assert result["key"] == "API_KEY"
    assert result["value"] == "secret123"


def test_unique_tokens_for_same_input():
    t1 = create_share_token("K", "V", PASS)
    t2 = create_share_token("K", "V", PASS)
    assert t1 != t2  # nonce-based encryption


def test_wrong_passphrase_raises():
    token = create_share_token("KEY", "val", PASS)
    with pytest.raises(Exception):
        decode_share_token(token, "wrongpass")


def test_expired_token_raises(monkeypatch):
    token = create_share_token("KEY", "val", PASS, ttl=1)
    # advance time past expiry
    monkeypatch.setattr("env_vault.share.time.time", lambda: time.time() + 10)
    with pytest.raises(ValueError, match="expired"):
        decode_share_token(token, PASS)


def test_save_and_load_token(tmp_path):
    token = create_share_token("X", "Y", PASS)
    p = tmp_path / "share.token"
    save_share_token(token, p)
    loaded = load_share_token(p)
    assert loaded == token


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_share_token(tmp_path / "nonexistent.token")


def test_decode_after_save_load_roundtrip(tmp_path):
    token = create_share_token("SECRET", "topsecret", PASS)
    p = tmp_path / "t.token"
    save_share_token(token, p)
    loaded = load_share_token(p)
    result = decode_share_token(loaded, PASS)
    assert result["key"] == "SECRET"
    assert result["value"] == "topsecret"
