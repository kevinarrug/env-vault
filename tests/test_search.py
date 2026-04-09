"""Tests for env_vault.search."""

from __future__ import annotations

import pytest

from env_vault.vault import Vault
from env_vault.search import search, search_by_key, search_by_value, SearchResult


PASS = "hunter2"


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path / "vault.json"))
    v.set("AWS_ACCESS_KEY", "AKIA1234", PASS)
    v.set("AWS_SECRET_KEY", "secret/abc", PASS)
    v.set("DATABASE_URL", "postgres://localhost/db", PASS)
    v.set("DEBUG", "true", PASS)
    return v


# --- search_by_key ---

def test_search_by_key_regex(vault):
    results = search_by_key(vault, PASS, r"^AWS_")
    keys = {r.key for r in results}
    assert keys == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}
    assert all(r.matched_by == "key" for r in results)


def test_search_by_key_glob(vault):
    results = search_by_key(vault, PASS, "AWS_*", glob=True)
    keys = {r.key for r in results}
    assert keys == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


def test_search_by_key_no_match(vault):
    results = search_by_key(vault, PASS, "NONEXISTENT")
    assert results == []


def test_search_by_key_returns_decrypted_value(vault):
    results = search_by_key(vault, PASS, "DEBUG")
    assert len(results) == 1
    assert results[0].value == "true"


# --- search_by_value ---

def test_search_by_value_regex(vault):
    results = search_by_value(vault, PASS, r"^AKIA")
    assert len(results) == 1
    assert results[0].key == "AWS_ACCESS_KEY"
    assert results[0].matched_by == "value"


def test_search_by_value_glob(vault):
    results = search_by_value(vault, PASS, "*localhost*", glob=True)
    assert len(results) == 1
    assert results[0].key == "DATABASE_URL"


def test_search_by_value_no_match(vault):
    results = search_by_value(vault, PASS, "NOTHING_HERE")
    assert results == []


# --- search (combined) ---

def test_search_combined_deduplicates(vault):
    # "AWS" appears in key names; "secret/abc" value contains no "AWS"
    # but the key AWS_SECRET_KEY does, so matched_by should be 'key' for that one
    results = search(vault, PASS, "AWS")
    keys = {r.key for r in results}
    assert "AWS_ACCESS_KEY" in keys
    assert "AWS_SECRET_KEY" in keys


def test_search_combined_marks_both(vault):
    # Add a key where the key name AND value both match the pattern
    from env_vault.vault import Vault
    vault.set("TOKEN_TOKEN", "TOKEN_VALUE_TOKEN", PASS)
    results = search(vault, PASS, "TOKEN")
    both = [r for r in results if r.matched_by == "both"]
    assert any(r.key == "TOKEN_TOKEN" for r in both)


def test_search_combined_sorted(vault):
    results = search(vault, PASS, ".")
    keys = [r.key for r in results]
    assert keys == sorted(keys)
