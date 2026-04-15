"""Tests for env_vault.env_severity."""

from __future__ import annotations

import pytest

from env_vault.env_severity import (
    get_severity,
    keys_by_level,
    list_severity,
    remove_severity,
    set_severity,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_severity_returns_true_when_new(vault_dir):
    assert set_severity(vault_dir, "API_KEY", "high") is True


def test_set_severity_returns_false_when_unchanged(vault_dir):
    set_severity(vault_dir, "API_KEY", "high")
    assert set_severity(vault_dir, "API_KEY", "high") is False


def test_set_severity_returns_true_when_changed(vault_dir):
    set_severity(vault_dir, "API_KEY", "low")
    assert set_severity(vault_dir, "API_KEY", "critical") is True


def test_get_severity_returns_value(vault_dir):
    set_severity(vault_dir, "DB_PASS", "critical")
    assert get_severity(vault_dir, "DB_PASS") == "critical"


def test_get_severity_missing_returns_none(vault_dir):
    assert get_severity(vault_dir, "MISSING_KEY") is None


def test_remove_severity_returns_true_when_found(vault_dir):
    set_severity(vault_dir, "TOKEN", "medium")
    assert remove_severity(vault_dir, "TOKEN") is True


def test_remove_severity_returns_false_when_not_found(vault_dir):
    assert remove_severity(vault_dir, "GHOST_KEY") is False


def test_remove_severity_clears_value(vault_dir):
    set_severity(vault_dir, "TOKEN", "medium")
    remove_severity(vault_dir, "TOKEN")
    assert get_severity(vault_dir, "TOKEN") is None


def test_list_severity_returns_all(vault_dir):
    set_severity(vault_dir, "A", "low")
    set_severity(vault_dir, "B", "critical")
    result = list_severity(vault_dir)
    assert result == {"A": "low", "B": "critical"}


def test_list_severity_empty_when_none(vault_dir):
    assert list_severity(vault_dir) == {}


def test_keys_by_level_returns_matching_keys(vault_dir):
    set_severity(vault_dir, "X", "high")
    set_severity(vault_dir, "Y", "low")
    set_severity(vault_dir, "Z", "high")
    assert keys_by_level(vault_dir, "high") == ["X", "Z"]


def test_keys_by_level_empty_when_no_match(vault_dir):
    set_severity(vault_dir, "A", "low")
    assert keys_by_level(vault_dir, "critical") == []


def test_set_severity_invalid_level_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid severity level"):
        set_severity(vault_dir, "KEY", "extreme")


def test_keys_by_level_invalid_level_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid severity level"):
        keys_by_level(vault_dir, "unknown")
