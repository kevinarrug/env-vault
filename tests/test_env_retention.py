"""Tests for env_vault.env_retention."""
import time
import pytest
from env_vault.env_retention import (
    set_retention,
    remove_retention,
    get_retention,
    list_retention,
    is_expired,
    expired_keys,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_retention_returns_true_when_new(vault_dir):
    assert set_retention(vault_dir, "API_KEY", 30) is True


def test_set_retention_returns_false_when_updated(vault_dir):
    set_retention(vault_dir, "API_KEY", 30)
    assert set_retention(vault_dir, "API_KEY", 60) is False


def test_set_retention_zero_raises(vault_dir):
    with pytest.raises(ValueError):
        set_retention(vault_dir, "API_KEY", 0)


def test_set_retention_negative_raises(vault_dir):
    with pytest.raises(ValueError):
        set_retention(vault_dir, "API_KEY", -5)


def test_get_retention_returns_info(vault_dir):
    set_retention(vault_dir, "SECRET", 7)
    info = get_retention(vault_dir, "SECRET")
    assert info is not None
    assert info["days"] == 7
    assert "set_at" in info


def test_get_retention_missing_returns_none(vault_dir):
    assert get_retention(vault_dir, "MISSING") is None


def test_remove_retention_returns_true_when_found(vault_dir):
    set_retention(vault_dir, "TOKEN", 14)
    assert remove_retention(vault_dir, "TOKEN") is True


def test_remove_retention_returns_false_when_missing(vault_dir):
    assert remove_retention(vault_dir, "GHOST") is False


def test_remove_retention_actually_removes(vault_dir):
    set_retention(vault_dir, "TOKEN", 14)
    remove_retention(vault_dir, "TOKEN")
    assert get_retention(vault_dir, "TOKEN") is None


def test_list_retention_returns_all(vault_dir):
    set_retention(vault_dir, "A", 1)
    set_retention(vault_dir, "B", 2)
    policies = list_retention(vault_dir)
    assert "A" in policies
    assert "B" in policies


def test_is_expired_false_when_just_set(vault_dir):
    set_retention(vault_dir, "KEY", 30)
    assert is_expired(vault_dir, "KEY") is False


def test_is_expired_true_when_past_deadline(vault_dir):
    set_retention(vault_dir, "OLD", 1)
    from env_vault import env_retention
    data = env_retention._load_retention(vault_dir)
    data["OLD"]["set_at"] = time.time() - 2 * 86400
    env_retention._save_retention(vault_dir, data)
    assert is_expired(vault_dir, "OLD") is True


def test_is_expired_false_when_no_policy(vault_dir):
    assert is_expired(vault_dir, "NOPOLICY") is False


def test_expired_keys_returns_correct_subset(vault_dir):
    set_retention(vault_dir, "FRESH", 30)
    set_retention(vault_dir, "STALE", 1)
    from env_vault import env_retention
    data = env_retention._load_retention(vault_dir)
    data["STALE"]["set_at"] = time.time() - 5 * 86400
    env_retention._save_retention(vault_dir, data)
    expired = expired_keys(vault_dir)
    assert "STALE" in expired
    assert "FRESH" not in expired
