"""Tests for env_vault.env_compare."""
from __future__ import annotations

import os
import pytest

from env_vault.env_compare import (
    CompareEntry,
    CompareResult,
    compare_vault_to_env,
)
from env_vault.vault import Vault


PASSPHRASE = "test-passphrase"


@pytest.fixture
def vault(tmp_path):
    v = Vault(str(tmp_path))
    v.set("KEY_A", "hello", PASSPHRASE)
    v.set("KEY_B", "world", PASSPHRASE)
    return v


# --- CompareEntry ---

def test_entry_match():
    e = CompareEntry(key="X", vault_value="v", env_value="v")
    assert e.matches
    assert e.status == "match"


def test_entry_mismatch():
    e = CompareEntry(key="X", vault_value="v", env_value="w")
    assert not e.matches
    assert e.status == "mismatch"


def test_entry_vault_only():
    e = CompareEntry(key="X", vault_value="v", env_value=None)
    assert e.status == "vault_only"


def test_entry_env_only():
    e = CompareEntry(key="X", vault_value=None, env_value="v")
    assert e.status == "env_only"


def test_entry_str_contains_key_and_status():
    e = CompareEntry(key="MY_KEY", vault_value="a", env_value="b")
    s = str(e)
    assert "MY_KEY" in s
    assert "mismatch" in s


# --- CompareResult ---

def test_compare_result_all_match_true():
    entries = [
        CompareEntry("A", "x", "x"),
        CompareEntry("B", "y", "y"),
    ]
    r = CompareResult(entries=entries)
    assert r.all_match


def test_compare_result_all_match_false():
    entries = [CompareEntry("A", "x", "z")]
    r = CompareResult(entries=entries)
    assert not r.all_match


def test_compare_result_summary_all_match():
    entries = [CompareEntry("A", "x", "x")]
    r = CompareResult(entries=entries)
    assert "match" in r.summary().lower()


def test_compare_result_summary_mismatches():
    entries = [CompareEntry("A", "x", "y"), CompareEntry("B", "p", "p")]
    r = CompareResult(entries=entries)
    assert "mismatch" in r.summary()


def test_compare_result_empty_summary():
    r = CompareResult(entries=[])
    assert r.summary() == "No keys to compare."


# --- compare_vault_to_env ---

def test_compare_matching_env(vault):
    env = {"KEY_A": "hello", "KEY_B": "world"}
    result = compare_vault_to_env(vault, PASSPHRASE, env=env)
    assert result.all_match
    assert len(result.entries) == 2


def test_compare_detects_mismatch(vault):
    env = {"KEY_A": "hello", "KEY_B": "DIFFERENT"}
    result = compare_vault_to_env(vault, PASSPHRASE, env=env)
    assert not result.all_match
    assert len(result.mismatches) == 1
    assert result.mismatches[0].key == "KEY_B"


def test_compare_vault_only(vault):
    env = {"KEY_A": "hello"}  # KEY_B missing from env
    result = compare_vault_to_env(vault, PASSPHRASE, env=env)
    assert any(e.status == "vault_only" for e in result.entries)


def test_compare_env_only(vault):
    env = {"KEY_A": "hello", "KEY_B": "world", "EXTRA": "extra"}
    result = compare_vault_to_env(vault, PASSPHRASE, env=env)
    env_only = [e for e in result.entries if e.status == "env_only"]
    assert any(e.key == "EXTRA" for e in env_only)


def test_compare_entries_sorted(vault):
    env = {"KEY_B": "world", "KEY_A": "hello"}
    result = compare_vault_to_env(vault, PASSPHRASE, env=env)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
