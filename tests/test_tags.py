"""Tests for env_vault.tags and env_vault.cli_tags."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_vault.cli_tags import tags_cmd
from env_vault.tags import (
    add_tag,
    all_tags,
    clear_tags_for_key,
    get_tags,
    keys_by_tag,
    remove_tag,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


# ── unit tests ────────────────────────────────────────────────────────────────

def test_add_tag_creates_entry(vault_dir):
    add_tag(vault_dir, "DB_URL", "database")
    assert "database" in get_tags(vault_dir, "DB_URL")


def test_add_tag_is_idempotent(vault_dir):
    add_tag(vault_dir, "DB_URL", "database")
    add_tag(vault_dir, "DB_URL", "database")
    assert get_tags(vault_dir, "DB_URL").count("database") == 1


def test_get_tags_missing_key_returns_empty(vault_dir):
    assert get_tags(vault_dir, "NONEXISTENT") == []


def test_remove_tag_returns_true_when_found(vault_dir):
    add_tag(vault_dir, "API_KEY", "secret")
    assert remove_tag(vault_dir, "API_KEY", "secret") is True
    assert "secret" not in get_tags(vault_dir, "API_KEY")


def test_remove_tag_returns_false_when_missing(vault_dir):
    assert remove_tag(vault_dir, "API_KEY", "ghost") is False


def test_remove_last_tag_cleans_key_entry(vault_dir):
    add_tag(vault_dir, "API_KEY", "only")
    remove_tag(vault_dir, "API_KEY", "only")
    assert "API_KEY" not in all_tags(vault_dir)


def test_keys_by_tag_returns_matching_keys(vault_dir):
    add_tag(vault_dir, "DB_URL", "database")
    add_tag(vault_dir, "DB_PASS", "database")
    add_tag(vault_dir, "API_KEY", "external")
    result = keys_by_tag(vault_dir, "database")
    assert set(result) == {"DB_URL", "DB_PASS"}


def test_keys_by_tag_no_match_returns_empty(vault_dir):
    assert keys_by_tag(vault_dir, "nonexistent") == []


def test_clear_tags_for_key(vault_dir):
    add_tag(vault_dir, "DB_URL", "database")
    add_tag(vault_dir, "DB_URL", "prod")
    clear_tags_for_key(vault_dir, "DB_URL")
    assert get_tags(vault_dir, "DB_URL") == []


# ── CLI tests ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_add_and_list(runner, vault_dir):
    result = runner.invoke(tags_cmd, ["add", "MY_KEY", "prod", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Tagged" in result.output

    result = runner.invoke(tags_cmd, ["list", "MY_KEY", "--vault-dir", vault_dir])
    assert "prod" in result.output


def test_cli_remove_existing_tag(runner, vault_dir):
    add_tag(vault_dir, "MY_KEY", "staging")
    result = runner.invoke(tags_cmd, ["remove", "MY_KEY", "staging", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_cli_remove_missing_tag(runner, vault_dir):
    result = runner.invoke(tags_cmd, ["remove", "MY_KEY", "ghost", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_cli_filter_by_tag(runner, vault_dir):
    add_tag(vault_dir, "A", "shared")
    add_tag(vault_dir, "B", "shared")
    result = runner.invoke(tags_cmd, ["filter", "shared", "--vault-dir", vault_dir])
    assert "A" in result.output
    assert "B" in result.output


def test_cli_show_all_empty(runner, vault_dir):
    result = runner.invoke(tags_cmd, ["show-all", "--vault-dir", vault_dir])
    assert "No tags" in result.output
