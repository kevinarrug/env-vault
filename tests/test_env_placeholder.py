"""Tests for env_vault.env_placeholder."""
from __future__ import annotations

import pytest

from env_vault.env_placeholder import (
    PLACEHOLDER_MARKER,
    PlaceholderResult,
    check_key,
    fill_placeholder,
    is_placeholder,
    list_placeholders,
    scan_vault,
)


# ---------------------------------------------------------------------------
# is_placeholder
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", [
    PLACEHOLDER_MARKER,
    "<MY_VALUE>",
    "{MY_VALUE}",
    "",
    "   ",
])
def test_is_placeholder_true(value: str) -> None:
    assert is_placeholder(value) is True


@pytest.mark.parametrize("value", [
    "realvalue",
    "secret123",
    "https://example.com",
])
def test_is_placeholder_false(value: str) -> None:
    assert is_placeholder(value) is False


# ---------------------------------------------------------------------------
# PlaceholderResult
# ---------------------------------------------------------------------------

def test_placeholder_result_str_placeholder() -> None:
    r = PlaceholderResult(key="FOO", is_placeholder=True)
    assert "placeholder" in str(r)
    assert "FOO" in str(r)


def test_placeholder_result_str_set() -> None:
    r = PlaceholderResult(key="BAR", is_placeholder=False)
    assert "set" in str(r)


# ---------------------------------------------------------------------------
# Vault integration helpers
# ---------------------------------------------------------------------------

class _FakeVault:
    def __init__(self, data: dict) -> None:
        self._data = dict(data)

    def list_keys(self):
        return list(self._data.keys())

    def get(self, key, passphrase):
        return self._data[key]

    def set(self, key, value, passphrase):
        self._data[key] = value


def test_check_key_is_placeholder() -> None:
    vault = _FakeVault({"DB_PASS": "<your-password>"})
    r = check_key(vault, "pass", "DB_PASS")
    assert r.is_placeholder is True
    assert r.key == "DB_PASS"


def test_check_key_is_not_placeholder() -> None:
    vault = _FakeVault({"DB_PASS": "s3cr3t"})
    r = check_key(vault, "pass", "DB_PASS")
    assert r.is_placeholder is False


def test_scan_vault_returns_all_keys() -> None:
    vault = _FakeVault({"A": "<fill>", "B": "real"})
    results = scan_vault(vault, "pass")
    assert len(results) == 2


def test_list_placeholders_filters_correctly() -> None:
    vault = _FakeVault({"A": "<fill>", "B": "real", "C": ""})
    keys = list_placeholders(vault, "pass")
    assert "A" in keys
    assert "C" in keys
    assert "B" not in keys


def test_fill_placeholder_returns_true_when_was_placeholder() -> None:
    vault = _FakeVault({"TOKEN": "<token>"})
    result = fill_placeholder(vault, "pass", "TOKEN", "abc123")
    assert result is True
    assert vault.get("TOKEN", "pass") == "abc123"


def test_fill_placeholder_returns_false_when_not_placeholder() -> None:
    vault = _FakeVault({"TOKEN": "already-set"})
    result = fill_placeholder(vault, "pass", "TOKEN", "new-value")
    assert result is False
    assert vault.get("TOKEN", "pass") == "new-value"
