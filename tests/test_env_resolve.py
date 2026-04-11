"""Tests for env_vault.env_resolve."""
from __future__ import annotations

import pytest

from env_vault.env_resolve import ResolveResult, resolve_value, resolve_all


SECRETS = {
    "BASE_URL": "https://example.com",
    "API_URL": "${BASE_URL}/api",
    "FULL_URL": "${API_URL}/v1",
    "PLAIN": "no-refs-here",
    "SELF_REF": "${SELF_REF}",
    "CYCLE_A": "${CYCLE_B}",
    "CYCLE_B": "${CYCLE_A}",
}


def test_resolve_no_references():
    r = resolve_value("PLAIN", "no-refs-here", SECRETS)
    assert r.resolved == "no-refs-here"
    assert r.references == []
    assert r.unresolved == []
    assert not r.has_unresolved


def test_resolve_single_reference():
    r = resolve_value("API_URL", "${BASE_URL}/api", SECRETS)
    assert r.resolved == "https://example.com/api"
    assert "BASE_URL" in r.references
    assert r.unresolved == []


def test_resolve_chained_references():
    r = resolve_value("FULL_URL", "${API_URL}/v1", SECRETS)
    assert r.resolved == "https://example.com/api/v1"
    assert "API_URL" in r.references


def test_resolve_missing_key_leaves_placeholder():
    r = resolve_value("X", "${MISSING}", SECRETS)
    assert r.resolved == "${MISSING}"
    assert "MISSING" in r.unresolved
    assert r.has_unresolved


def test_resolve_self_reference_leaves_placeholder():
    r = resolve_value("SELF_REF", "${SELF_REF}", SECRETS)
    assert r.resolved == "${SELF_REF}"
    assert "SELF_REF" in r.unresolved


def test_resolve_cycle_leaves_placeholder():
    r = resolve_value("CYCLE_A", "${CYCLE_B}", SECRETS)
    assert "${" in r.resolved  # cycle not fully expanded


def test_resolve_all_returns_all_keys():
    results = resolve_all(SECRETS)
    assert set(results.keys()) == set(SECRETS.keys())


def test_resolve_all_plain_value_unchanged():
    results = resolve_all(SECRETS)
    assert results["PLAIN"].resolved == "no-refs-here"


def test_resolve_all_expands_chained():
    results = resolve_all(SECRETS)
    assert results["FULL_URL"].resolved == "https://example.com/api/v1"


def test_resolve_result_str_returns_resolved():
    r = ResolveResult(key="K", raw="${A}", resolved="hello", references=["A"])
    assert str(r) == "hello"


def test_resolve_multiple_refs_in_one_value():
    secrets = {"HOST": "localhost", "PORT": "5432", "DSN": "${HOST}:${PORT}"}
    r = resolve_value("DSN", "${HOST}:${PORT}", secrets)
    assert r.resolved == "localhost:5432"
    assert set(r.references) == {"HOST", "PORT"}
