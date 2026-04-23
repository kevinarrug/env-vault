"""Tests for env_vault.env_origin."""

from __future__ import annotations

import pytest

from env_vault.env_origin import (
    get_origin,
    keys_by_origin,
    list_origins,
    remove_origin,
    set_origin,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_origin_returns_true_when_new(vault_dir):
    assert set_origin(vault_dir, "API_KEY", "aws") is True


def test_set_origin_returns_false_when_unchanged(vault_dir):
    set_origin(vault_dir, "API_KEY", "aws")
    assert set_origin(vault_dir, "API_KEY", "aws") is False


def test_set_origin_returns_true_when_changed(vault_dir):
    set_origin(vault_dir, "API_KEY", "aws")
    assert set_origin(vault_dir, "API_KEY", "gcp") is True


def test_get_origin_returns_value(vault_dir):
    set_origin(vault_dir, "DB_PASS", "heroku")
    assert get_origin(vault_dir, "DB_PASS") == "heroku"


def test_get_origin_missing_returns_none(vault_dir):
    assert get_origin(vault_dir, "MISSING") is None


def test_remove_origin_returns_true_when_found(vault_dir):
    set_origin(vault_dir, "TOKEN", "github")
    assert remove_origin(vault_dir, "TOKEN") is True


def test_remove_origin_returns_false_when_missing(vault_dir):
    assert remove_origin(vault_dir, "GHOST") is False


def test_remove_origin_deletes_entry(vault_dir):
    set_origin(vault_dir, "TOKEN", "github")
    remove_origin(vault_dir, "TOKEN")
    assert get_origin(vault_dir, "TOKEN") is None


def test_list_origins_returns_all(vault_dir):
    set_origin(vault_dir, "A", "aws")
    set_origin(vault_dir, "B", "gcp")
    result = list_origins(vault_dir)
    assert result == {"A": "aws", "B": "gcp"}


def test_list_origins_empty_when_none(vault_dir):
    assert list_origins(vault_dir) == {}


def test_keys_by_origin_returns_matching(vault_dir):
    set_origin(vault_dir, "A", "aws")
    set_origin(vault_dir, "B", "gcp")
    set_origin(vault_dir, "C", "aws")
    assert keys_by_origin(vault_dir, "aws") == ["A", "C"]


def test_keys_by_origin_empty_when_no_match(vault_dir):
    set_origin(vault_dir, "A", "aws")
    assert keys_by_origin(vault_dir, "azure") == []


def test_keys_by_origin_sorted(vault_dir):
    set_origin(vault_dir, "Z_KEY", "aws")
    set_origin(vault_dir, "A_KEY", "aws")
    result = keys_by_origin(vault_dir, "aws")
    assert result == ["A_KEY", "Z_KEY"]
