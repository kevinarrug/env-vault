"""Tests for env_vault.expiry."""

from __future__ import annotations

import time

import pytest

from env_vault.expiry import (
    ExpiryInfo,
    get_expiry,
    list_expiring,
    purge_expired,
    remove_expiry,
    set_expiry,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# set_expiry / get_expiry
# ---------------------------------------------------------------------------

def test_set_expiry_returns_future_timestamp(vault_dir):
    before = time.time()
    ts = set_expiry(vault_dir, "API_KEY", 60)
    assert ts > before
    assert ts <= time.time() + 61


def test_set_expiry_zero_raises(vault_dir):
    with pytest.raises(ValueError):
        set_expiry(vault_dir, "API_KEY", 0)


def test_set_expiry_negative_raises(vault_dir):
    with pytest.raises(ValueError):
        set_expiry(vault_dir, "API_KEY", -5)


def test_get_expiry_returns_info(vault_dir):
    set_expiry(vault_dir, "DB_PASS", 120)
    info = get_expiry(vault_dir, "DB_PASS")
    assert isinstance(info, ExpiryInfo)
    assert info.key == "DB_PASS"
    assert not info.is_expired
    assert info.remaining_seconds > 0


def test_get_expiry_missing_key_returns_none(vault_dir):
    assert get_expiry(vault_dir, "NONEXISTENT") is None


def test_expiry_info_is_expired_for_past_timestamp(vault_dir):
    info = ExpiryInfo(key="OLD_KEY", expires_at=time.time() - 1)
    assert info.is_expired
    assert info.remaining_seconds == 0.0


def test_expiry_info_str_contains_key(vault_dir):
    set_expiry(vault_dir, "TOKEN", 300)
    info = get_expiry(vault_dir, "TOKEN")
    assert "TOKEN" in str(info)
    assert "remaining" in str(info)


# ---------------------------------------------------------------------------
# remove_expiry
# ---------------------------------------------------------------------------

def test_remove_expiry_returns_true_when_found(vault_dir):
    set_expiry(vault_dir, "SECRET", 60)
    assert remove_expiry(vault_dir, "SECRET") is True


def test_remove_expiry_returns_false_when_missing(vault_dir):
    assert remove_expiry(vault_dir, "GHOST") is False


def test_remove_expiry_clears_entry(vault_dir):
    set_expiry(vault_dir, "SECRET", 60)
    remove_expiry(vault_dir, "SECRET")
    assert get_expiry(vault_dir, "SECRET") is None


# ---------------------------------------------------------------------------
# list_expiring
# ---------------------------------------------------------------------------

def test_list_expiring_empty(vault_dir):
    assert list_expiring(vault_dir) == []


def test_list_expiring_sorted_by_expiry(vault_dir):
    set_expiry(vault_dir, "LATE_KEY", 300)
    set_expiry(vault_dir, "SOON_KEY", 10)
    infos = list_expiring(vault_dir)
    assert infos[0].key == "SOON_KEY"
    assert infos[1].key == "LATE_KEY"


# ---------------------------------------------------------------------------
# purge_expired
# ---------------------------------------------------------------------------

def test_purge_expired_removes_past_entries(vault_dir):
    # Manually inject an already-expired timestamp
    from env_vault.expiry import _save_expiry
    _save_expiry(vault_dir, {"STALE": time.time() - 10, "FRESH": time.time() + 600})
    purged = purge_expired(vault_dir)
    assert "STALE" in purged
    assert "FRESH" not in purged
    assert get_expiry(vault_dir, "FRESH") is not None
    assert get_expiry(vault_dir, "STALE") is None


def test_purge_expired_empty_vault(vault_dir):
    assert purge_expired(vault_dir) == []
