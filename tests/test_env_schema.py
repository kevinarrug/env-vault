"""Tests for env_vault.env_schema."""
from __future__ import annotations

import pytest

from env_vault.env_schema import SchemaRule, SchemaViolation, SchemaResult, validate


# ---------------------------------------------------------------------------
# SchemaResult helpers
# ---------------------------------------------------------------------------

def test_schema_result_passed_when_no_violations():
    r = SchemaResult()
    assert r.passed is True


def test_schema_result_failed_when_violations_present():
    r = SchemaResult(violations=[SchemaViolation("KEY", "bad")])
    assert r.passed is False


def test_schema_result_summary_no_violations():
    r = SchemaResult()
    assert "passed" in r.summary()


def test_schema_result_summary_lists_violations():
    r = SchemaResult(violations=[SchemaViolation("FOO", "too short")])
    summary = r.summary()
    assert "FOO" in summary
    assert "too short" in summary


def test_violation_str_format():
    v = SchemaViolation("DB_PASS", "required key is missing")
    assert str(v) == "DB_PASS: required key is missing"


# ---------------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------------

def test_validate_passes_clean_data():
    rules = [SchemaRule(key="API_KEY", required=True, min_length=8)]
    data = {"API_KEY": "supersecret"}
    result = validate(data, rules)
    assert result.passed


def test_validate_missing_required_key():
    rules = [SchemaRule(key="API_KEY", required=True)]
    result = validate({}, rules)
    assert not result.passed
    assert any("missing" in str(v) for v in result.violations)


def test_validate_optional_missing_key_passes():
    rules = [SchemaRule(key="OPTIONAL_KEY", required=False)]
    result = validate({}, rules)
    assert result.passed


def test_validate_min_length_violation():
    rules = [SchemaRule(key="SECRET", min_length=10)]
    result = validate({"SECRET": "short"}, rules)
    assert not result.passed
    assert any("too short" in str(v) for v in result.violations)


def test_validate_max_length_violation():
    rules = [SchemaRule(key="TOKEN", max_length=5)]
    result = validate({"TOKEN": "toolongvalue"}, rules)
    assert not result.passed
    assert any("too long" in str(v) for v in result.violations)


def test_validate_pattern_match_passes():
    rules = [SchemaRule(key="PORT", pattern=r"\d+")]
    result = validate({"PORT": "8080"}, rules)
    assert result.passed


def test_validate_pattern_mismatch_violation():
    rules = [SchemaRule(key="PORT", pattern=r"\d+")]
    result = validate({"PORT": "not-a-number"}, rules)
    assert not result.passed
    assert any("pattern" in str(v) for v in result.violations)


def test_validate_multiple_violations_collected():
    rules = [
        SchemaRule(key="A", required=True),
        SchemaRule(key="B", required=True),
    ]
    result = validate({}, rules)
    assert len(result.violations) == 2


def test_validate_extra_keys_ignored():
    rules = [SchemaRule(key="KNOWN", required=True)]
    data = {"KNOWN": "value", "EXTRA": "whatever"}
    result = validate(data, rules)
    assert result.passed
