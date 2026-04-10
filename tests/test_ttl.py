"""Tests for env_vault.ttl."""

from __future__ import annotations

import time

import pytest

from env_vault.ttl import (
    get_ttl,
    is_expired,
    list_ttls,
    purge_expired,
    remove_ttl,
    set_ttl,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_ttl_returns_future_timestamp(vault_dir):
    before = time.time()
    expires_at = set_ttl(vault_dir, "MY_KEY", 60)
    assert expires_at > before + 59


def test_set_ttl_zero_raises(vault_dir):
    with pytest.raises(ValueError, match="positive"):
        set_ttl(vault_dir, "KEY", 0)


def test_set_ttl_negative_raises(vault_dir):
    with pytest.raises(ValueError):
        set_ttl(vault_dir, "KEY", -10)


def test_get_ttl_returns_remaining_seconds(vault_dir):
    set_ttl(vault_dir, "KEY", 120)
    remaining = get_ttl(vault_dir, "KEY")
    assert remaining is not None
    assert 119 < remaining <= 120


def test_get_ttl_missing_key_returns_none(vault_dir):
    assert get_ttl(vault_dir, "MISSING") is None


def test_is_expired_false_for_future_key(vault_dir):
    set_ttl(vault_dir, "KEY", 300)
    assert not is_expired(vault_dir, "KEY")


def test_is_expired_true_for_past_key(vault_dir, monkeypatch):
    set_ttl(vault_dir, "KEY", 1)
    # Simulate time passing by patching time.time
    monkeypatch.setattr(time, "time", lambda: time.time.__wrapped__() + 10)
    # Re-import to pick up monkeypatched time
    import env_vault.ttl as ttl_mod
    original = ttl_mod.time.time
    ttl_mod.time.time = lambda: original() + 10
    try:
        assert is_expired(vault_dir, "KEY")
    finally:
        ttl_mod.time.time = original


def test_is_expired_false_for_key_without_ttl(vault_dir):
    assert not is_expired(vault_dir, "NO_TTL")


def test_remove_ttl_returns_true_when_found(vault_dir):
    set_ttl(vault_dir, "KEY", 60)
    assert remove_ttl(vault_dir, "KEY") is True


def test_remove_ttl_returns_false_when_missing(vault_dir):
    assert remove_ttl(vault_dir, "GHOST") is False


def test_remove_ttl_then_get_returns_none(vault_dir):
    set_ttl(vault_dir, "KEY", 60)
    remove_ttl(vault_dir, "KEY")
    assert get_ttl(vault_dir, "KEY") is None


def test_list_ttls_returns_all_keys(vault_dir):
    set_ttl(vault_dir, "A", 60)
    set_ttl(vault_dir, "B", 120)
    ttls = list_ttls(vault_dir)
    assert set(ttls.keys()) == {"A", "B"}


def test_list_ttls_empty_vault(vault_dir):
    assert list_ttls(vault_dir) == {}


def test_purge_expired_removes_only_expired(vault_dir):
    import env_vault.ttl as ttl_mod

    set_ttl(vault_dir, "OLD", 1)
    set_ttl(vault_dir, "NEW", 300)

    original = ttl_mod.time.time
    ttl_mod.time.time = lambda: original() + 10
    try:
        expired = purge_expired(vault_dir)
    finally:
        ttl_mod.time.time = original

    assert "OLD" in expired
    assert "NEW" not in expired
    assert get_ttl(vault_dir, "NEW") is not None


def test_purge_expired_returns_empty_when_nothing_expired(vault_dir):
    set_ttl(vault_dir, "KEY", 300)
    assert purge_expired(vault_dir) == []
