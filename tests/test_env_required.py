"""Tests for env_vault.env_required."""
import pytest
from env_vault.env_required import (
    mark_required,
    unmark_required,
    is_required,
    list_required,
    check_required,
    RequiredCheckResult,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_mark_required_returns_true_when_new(vault_dir):
    assert mark_required(vault_dir, "API_KEY") is True


def test_mark_required_returns_false_when_duplicate(vault_dir):
    mark_required(vault_dir, "API_KEY")
    assert mark_required(vault_dir, "API_KEY") is False


def test_is_required_true_after_mark(vault_dir):
    mark_required(vault_dir, "DB_URL")
    assert is_required(vault_dir, "DB_URL") is True


def test_is_required_false_before_mark(vault_dir):
    assert is_required(vault_dir, "DB_URL") is False


def test_unmark_required_returns_true_when_found(vault_dir):
    mark_required(vault_dir, "SECRET")
    assert unmark_required(vault_dir, "SECRET") is True


def test_unmark_required_returns_false_when_not_found(vault_dir):
    assert unmark_required(vault_dir, "SECRET") is False


def test_is_required_false_after_unmark(vault_dir):
    mark_required(vault_dir, "TOKEN")
    unmark_required(vault_dir, "TOKEN")
    assert is_required(vault_dir, "TOKEN") is False


def test_list_required_returns_sorted(vault_dir):
    mark_required(vault_dir, "Z_KEY")
    mark_required(vault_dir, "A_KEY")
    mark_required(vault_dir, "M_KEY")
    assert list_required(vault_dir) == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_required_empty_when_none(vault_dir):
    assert list_required(vault_dir) == []


def test_check_required_passed_when_all_present(vault_dir):
    mark_required(vault_dir, "API_KEY")
    mark_required(vault_dir, "DB_URL")
    result = check_required(vault_dir, ["API_KEY", "DB_URL", "EXTRA"])
    assert result.passed is True
    assert result.missing == []


def test_check_required_fails_when_key_missing(vault_dir):
    mark_required(vault_dir, "API_KEY")
    mark_required(vault_dir, "DB_URL")
    result = check_required(vault_dir, ["API_KEY"])
    assert result.passed is False
    assert "DB_URL" in result.missing


def test_check_required_present_list_correct(vault_dir):
    mark_required(vault_dir, "API_KEY")
    mark_required(vault_dir, "DB_URL")
    result = check_required(vault_dir, ["API_KEY"])
    assert "API_KEY" in result.present
    assert "DB_URL" not in result.present


def test_check_required_summary_no_missing(vault_dir):
    mark_required(vault_dir, "KEY")
    result = check_required(vault_dir, ["KEY"])
    assert result.summary() == "All required keys are present."


def test_check_required_summary_lists_missing(vault_dir):
    mark_required(vault_dir, "MISSING_KEY")
    result = check_required(vault_dir, [])
    assert "MISSING_KEY" in result.summary()


def test_check_required_no_required_keys_always_passes(vault_dir):
    result = check_required(vault_dir, [])
    assert result.passed is True
