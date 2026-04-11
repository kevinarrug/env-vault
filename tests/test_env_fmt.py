"""Tests for env_vault.env_fmt."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from env_vault.env_fmt import (
    apply_format,
    fmt_key,
    fmt_all,
    FmtResult,
    FmtReport,
)


# ---------------------------------------------------------------------------
# apply_format
# ---------------------------------------------------------------------------

def test_apply_format_strip():
    assert apply_format("  hello  ", "strip") == "hello"


def test_apply_format_upper():
    assert apply_format("hello", "upper") == "HELLO"


def test_apply_format_lower():
    assert apply_format("HELLO", "lower") == "hello"


def test_apply_format_strip_quotes_double():
    assert apply_format('"value"', "strip_quotes") == "value"


def test_apply_format_strip_quotes_single():
    assert apply_format("'value'", "strip_quotes") == "value"


def test_apply_format_unknown_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        apply_format("x", "nonexistent")


# ---------------------------------------------------------------------------
# FmtResult
# ---------------------------------------------------------------------------

def test_fmt_result_str_changed():
    r = FmtResult(key="FOO", original="foo", formatted="FOO", changed=True)
    assert "changed" in str(r)
    assert "FOO" in str(r)


def test_fmt_result_str_unchanged():
    r = FmtResult(key="FOO", original="FOO", formatted="FOO", changed=False)
    assert "unchanged" in str(r)


# ---------------------------------------------------------------------------
# FmtReport
# ---------------------------------------------------------------------------

def test_fmt_report_changed_keys():
    report = FmtReport(results=[
        FmtResult("A", "a", "A", True),
        FmtResult("B", "B", "B", False),
    ])
    assert report.changed_keys == ["A"]


def test_fmt_report_summary_all_formatted():
    report = FmtReport(results=[
        FmtResult("A", "A", "A", False),
    ])
    assert "already formatted" in report.summary()


def test_fmt_report_summary_with_changes():
    report = FmtReport(results=[
        FmtResult("A", "a", "A", True),
        FmtResult("B", "B", "B", False),
    ])
    assert "1/2" in report.summary()


# ---------------------------------------------------------------------------
# fmt_key
# ---------------------------------------------------------------------------

def _make_vault(data: dict) -> MagicMock:
    vault = MagicMock()
    vault.get.side_effect = lambda k, _p: data[k]
    return vault


def test_fmt_key_changed_calls_set():
    vault = _make_vault({"FOO": "  hello  "})
    result = fmt_key(vault, "pass", "FOO", "strip")
    assert result.changed is True
    assert result.formatted == "hello"
    vault.set.assert_called_once_with("FOO", "hello", "pass")


def test_fmt_key_unchanged_does_not_call_set():
    vault = _make_vault({"FOO": "hello"})
    result = fmt_key(vault, "pass", "FOO", "strip")
    assert result.changed is False
    vault.set.assert_not_called()


# ---------------------------------------------------------------------------
# fmt_all
# ---------------------------------------------------------------------------

def test_fmt_all_processes_all_keys():
    vault = _make_vault({"A": " a ", "B": "b"})
    vault.list_keys.return_value = ["A", "B"]
    report = fmt_all(vault, "pass", "strip")
    assert len(report.results) == 2
    assert "A" in report.changed_keys
    assert "B" not in report.changed_keys
