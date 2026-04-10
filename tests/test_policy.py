"""Tests for env_vault.policy."""

import json
import pytest

from env_vault.policy import (
    PolicyViolation,
    PolicyResult,
    enforce_policy,
    load_policy,
    save_policy,
)


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def test_policy_result_passed_when_no_violations():
    result = PolicyResult()
    assert result.passed is True


def test_policy_result_failed_when_violations_present():
    result = PolicyResult(violations=[PolicyViolation("KEY", "required_keys", "missing")])
    assert result.passed is False


def test_policy_result_summary_no_violations():
    assert "passed" in PolicyResult().summary()


def test_policy_result_summary_lists_violations():
    v = PolicyViolation("SECRET", "required_keys", "key is missing from vault")
    result = PolicyResult(violations=[v])
    summary = result.summary()
    assert "1 violation" in summary
    assert "SECRET" in summary


def test_violation_str_format():
    v = PolicyViolation("MY_KEY", "key_pattern", "does not match")
    assert "[key_pattern]" in str(v)
    assert "MY_KEY" in str(v)


# ---------------------------------------------------------------------------
# enforce_policy
# ---------------------------------------------------------------------------

def test_required_keys_passes_when_present():
    result = enforce_policy({"DB_HOST": "localhost"}, {"required_keys": ["DB_HOST"]})
    assert result.passed


def test_required_keys_fails_when_missing():
    result = enforce_policy({}, {"required_keys": ["DB_HOST"]})
    assert not result.passed
    assert any(v.key == "DB_HOST" for v in result.violations)


def test_forbidden_regex_flags_matching_key():
    result = enforce_policy({"DEV_SECRET": "x"}, {"forbidden_regex": ["^DEV_"]})
    assert not result.passed
    assert result.violations[0].rule == "forbidden_regex"


def test_forbidden_regex_allows_non_matching_key():
    result = enforce_policy({"PROD_SECRET": "x"}, {"forbidden_regex": ["^DEV_"]})
    assert result.passed


def test_value_min_length_passes():
    result = enforce_policy({"KEY": "longvalue"}, {"value_min_length": 5})
    assert result.passed


def test_value_min_length_fails():
    result = enforce_policy({"KEY": "abc"}, {"value_min_length": 8})
    assert not result.passed
    assert result.violations[0].rule == "value_min_length"


def test_key_pattern_passes():
    result = enforce_policy({"MY_KEY": "v"}, {"key_pattern": "[A-Z_]+"})
    assert result.passed


def test_key_pattern_fails_on_lowercase():
    result = enforce_policy({"mykey": "v"}, {"key_pattern": "[A-Z_]+"})
    assert not result.passed
    assert result.violations[0].rule == "key_pattern"


def test_empty_policy_always_passes():
    result = enforce_policy({"anything": "value"}, {})
    assert result.passed


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def test_save_and_load_policy(tmp_path):
    policy = {"required_keys": ["APP_ENV"], "value_min_length": 4}
    save_policy(str(tmp_path), policy)
    loaded = load_policy(str(tmp_path))
    assert loaded == policy


def test_load_policy_missing_file_returns_empty(tmp_path):
    assert load_policy(str(tmp_path)) == {}
