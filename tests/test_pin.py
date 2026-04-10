"""Tests for env_vault.pin module."""

from __future__ import annotations

import pytest

from env_vault.pin import (
    check_pin,
    get_pin,
    list_pins,
    pin_key,
    unpin_key,
    validate_all,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_pin_key_returns_true_when_new(vault_dir):
    assert pin_key(vault_dir, "API_KEY", r"[A-Z0-9]{32}") is True


def test_pin_key_returns_false_when_updated(vault_dir):
    pin_key(vault_dir, "API_KEY", r"[A-Z0-9]{32}")
    assert pin_key(vault_dir, "API_KEY", r"[A-Z0-9]{64}") is False


def test_get_pin_returns_pattern(vault_dir):
    pin_key(vault_dir, "SECRET", r".{8,}")
    assert get_pin(vault_dir, "SECRET") == r".{8,}"


def test_get_pin_missing_returns_none(vault_dir):
    assert get_pin(vault_dir, "MISSING") is None


def test_unpin_key_returns_true_when_found(vault_dir):
    pin_key(vault_dir, "TOKEN", r".*")
    assert unpin_key(vault_dir, "TOKEN") is True


def test_unpin_key_returns_false_when_missing(vault_dir):
    assert unpin_key(vault_dir, "GHOST") is False


def test_unpin_removes_key(vault_dir):
    pin_key(vault_dir, "DB_PASS", r".{12,}")
    unpin_key(vault_dir, "DB_PASS")
    assert get_pin(vault_dir, "DB_PASS") is None


def test_list_pins_empty(vault_dir):
    assert list_pins(vault_dir) == {}


def test_list_pins_returns_all(vault_dir):
    pin_key(vault_dir, "A", r"\d+")
    pin_key(vault_dir, "B", r"[a-z]+")
    pins = list_pins(vault_dir)
    assert pins == {"A": r"\d+", "B": r"[a-z]+"}


def test_check_pin_passes_matching_value(vault_dir):
    pin_key(vault_dir, "PORT", r"\d{4,5}")
    assert check_pin(vault_dir, "PORT", "8080") is True


def test_check_pin_fails_non_matching_value(vault_dir):
    pin_key(vault_dir, "PORT", r"\d{4,5}")
    assert check_pin(vault_dir, "PORT", "abc") is False


def test_check_pin_unpinned_key_always_passes(vault_dir):
    assert check_pin(vault_dir, "ANYTHING", "whatever") is True


def test_validate_all_no_violations(vault_dir):
    pin_key(vault_dir, "KEY", r"[A-Z]+")
    violations = validate_all(vault_dir, {"KEY": "HELLO"})
    assert violations == {}


def test_validate_all_reports_violations(vault_dir):
    pin_key(vault_dir, "KEY", r"[A-Z]+")
    violations = validate_all(vault_dir, {"KEY": "hello"})
    assert "KEY" in violations


def test_validate_all_missing_value_treated_as_empty(vault_dir):
    pin_key(vault_dir, "REQUIRED", r".+")
    violations = validate_all(vault_dir, {})
    assert "REQUIRED" in violations
