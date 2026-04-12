"""Tests for env_vault.env_version."""

import pytest

from env_vault.env_version import (
    get_pin,
    is_pinned,
    list_pins,
    pin_version,
    unpin_version,
    VersionPin,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_pin_version_returns_true_when_new(vault_dir):
    assert pin_version(vault_dir, "API_KEY", 2) is True


def test_pin_version_returns_false_when_updated(vault_dir):
    pin_version(vault_dir, "API_KEY", 2)
    assert pin_version(vault_dir, "API_KEY", 3) is False


def test_get_pin_returns_version_pin(vault_dir):
    pin_version(vault_dir, "API_KEY", 5, note="stable release")
    pin = get_pin(vault_dir, "API_KEY")
    assert isinstance(pin, VersionPin)
    assert pin.key == "API_KEY"
    assert pin.pinned_index == 5
    assert pin.note == "stable release"


def test_get_pin_missing_returns_none(vault_dir):
    assert get_pin(vault_dir, "MISSING") is None


def test_is_pinned_true_after_pin(vault_dir):
    pin_version(vault_dir, "DB_URL", 1)
    assert is_pinned(vault_dir, "DB_URL") is True


def test_is_pinned_false_before_pin(vault_dir):
    assert is_pinned(vault_dir, "DB_URL") is False


def test_unpin_returns_true_when_found(vault_dir):
    pin_version(vault_dir, "SECRET", 0)
    assert unpin_version(vault_dir, "SECRET") is True


def test_unpin_returns_false_when_not_found(vault_dir):
    assert unpin_version(vault_dir, "GHOST") is False


def test_unpin_removes_entry(vault_dir):
    pin_version(vault_dir, "TOKEN", 3)
    unpin_version(vault_dir, "TOKEN")
    assert is_pinned(vault_dir, "TOKEN") is False


def test_list_pins_empty(vault_dir):
    assert list_pins(vault_dir) == []


def test_list_pins_sorted_by_key(vault_dir):
    pin_version(vault_dir, "Z_KEY", 1)
    pin_version(vault_dir, "A_KEY", 2)
    pin_version(vault_dir, "M_KEY", 0)
    pins = list_pins(vault_dir)
    assert [p.key for p in pins] == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_pins_returns_correct_indexes(vault_dir):
    pin_version(vault_dir, "FOO", 7, note="pinned")
    pins = list_pins(vault_dir)
    assert pins[0].pinned_index == 7
    assert pins[0].note == "pinned"


def test_pin_negative_index_raises(vault_dir):
    with pytest.raises(ValueError, match="index must be >= 0"):
        pin_version(vault_dir, "BAD", -1)


def test_version_pin_str(vault_dir):
    pin = VersionPin(key="API_KEY", pinned_index=3, note="v1.0")
    assert "API_KEY" in str(pin)
    assert "3" in str(pin)
    assert "v1.0" in str(pin)


def test_pin_zero_index_is_valid(vault_dir):
    assert pin_version(vault_dir, "FIRST", 0) is True
    assert get_pin(vault_dir, "FIRST").pinned_index == 0
