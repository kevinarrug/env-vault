"""Tests for env_vault.env_comment."""

from __future__ import annotations

import pytest

from env_vault.env_comment import (
    get_comment,
    keys_with_comments,
    list_comments,
    remove_comment,
    set_comment,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_comment_returns_true_when_new(vault_dir):
    assert set_comment(vault_dir, "DB_HOST", "Primary database host") is True


def test_set_comment_returns_false_when_updated(vault_dir):
    set_comment(vault_dir, "DB_HOST", "old")
    assert set_comment(vault_dir, "DB_HOST", "new") is False


def test_get_comment_returns_value(vault_dir):
    set_comment(vault_dir, "API_KEY", "Third-party API key")
    assert get_comment(vault_dir, "API_KEY") == "Third-party API key"


def test_get_comment_missing_returns_none(vault_dir):
    assert get_comment(vault_dir, "MISSING") is None


def test_remove_comment_returns_true_when_found(vault_dir):
    set_comment(vault_dir, "X", "some comment")
    assert remove_comment(vault_dir, "X") is True


def test_remove_comment_returns_false_when_missing(vault_dir):
    assert remove_comment(vault_dir, "GHOST") is False


def test_remove_comment_deletes_entry(vault_dir):
    set_comment(vault_dir, "Y", "bye")
    remove_comment(vault_dir, "Y")
    assert get_comment(vault_dir, "Y") is None


def test_list_comments_returns_all(vault_dir):
    set_comment(vault_dir, "A", "alpha")
    set_comment(vault_dir, "B", "beta")
    result = list_comments(vault_dir)
    assert result == {"A": "alpha", "B": "beta"}


def test_list_comments_empty_vault(vault_dir):
    assert list_comments(vault_dir) == {}


def test_keys_with_comments_sorted(vault_dir):
    set_comment(vault_dir, "Z", "z")
    set_comment(vault_dir, "A", "a")
    set_comment(vault_dir, "M", "m")
    assert keys_with_comments(vault_dir) == ["A", "M", "Z"]


def test_update_comment_persists_new_value(vault_dir):
    set_comment(vault_dir, "DB_PORT", "original")
    set_comment(vault_dir, "DB_PORT", "updated")
    assert get_comment(vault_dir, "DB_PORT") == "updated"
