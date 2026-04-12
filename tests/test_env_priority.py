"""Tests for env_vault.env_priority."""
import pytest
from click.testing import CliRunner

from env_vault.env_priority import (
    VALID_PRIORITIES,
    get_priority,
    keys_by_priority,
    list_priorities,
    remove_priority,
    set_priority,
)
from env_vault.cli_priority import priority_cmd


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_priority_returns_true_when_new(vault_dir):
    assert set_priority(vault_dir, "API_KEY", "high") is True


def test_set_priority_returns_false_when_unchanged(vault_dir):
    set_priority(vault_dir, "API_KEY", "high")
    assert set_priority(vault_dir, "API_KEY", "high") is False


def test_set_priority_returns_true_when_changed(vault_dir):
    set_priority(vault_dir, "API_KEY", "high")
    assert set_priority(vault_dir, "API_KEY", "low") is True


def test_get_priority_returns_value(vault_dir):
    set_priority(vault_dir, "DB_PASS", "critical")
    assert get_priority(vault_dir, "DB_PASS") == "critical"


def test_get_priority_missing_returns_none(vault_dir):
    assert get_priority(vault_dir, "MISSING") is None


def test_remove_priority_returns_true_when_found(vault_dir):
    set_priority(vault_dir, "TOKEN", "normal")
    assert remove_priority(vault_dir, "TOKEN") is True


def test_remove_priority_returns_false_when_missing(vault_dir):
    assert remove_priority(vault_dir, "GHOST") is False


def test_remove_priority_clears_key(vault_dir):
    set_priority(vault_dir, "X", "low")
    remove_priority(vault_dir, "X")
    assert get_priority(vault_dir, "X") is None


def test_list_priorities_returns_all(vault_dir):
    set_priority(vault_dir, "A", "high")
    set_priority(vault_dir, "B", "low")
    result = list_priorities(vault_dir)
    assert result == {"A": "high", "B": "low"}


def test_list_priorities_empty(vault_dir):
    assert list_priorities(vault_dir) == {}


def test_keys_by_priority_returns_matching(vault_dir):
    set_priority(vault_dir, "A", "high")
    set_priority(vault_dir, "B", "low")
    set_priority(vault_dir, "C", "high")
    assert keys_by_priority(vault_dir, "high") == ["A", "C"]


def test_keys_by_priority_empty_when_none(vault_dir):
    assert keys_by_priority(vault_dir, "critical") == []


def test_set_invalid_priority_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid priority"):
        set_priority(vault_dir, "KEY", "extreme")


def test_keys_by_priority_invalid_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid priority"):
        keys_by_priority(vault_dir, "ultra")


# CLI tests

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_reports_set(runner, vault_dir):
    result = runner.invoke(priority_cmd, ["set", "MY_KEY", "high", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "set to 'high'" in result.output


def test_cli_set_reports_already_set(runner, vault_dir):
    runner.invoke(priority_cmd, ["set", "MY_KEY", "high", "--vault-dir", vault_dir])
    result = runner.invoke(priority_cmd, ["set", "MY_KEY", "high", "--vault-dir", vault_dir])
    assert "already" in result.output


def test_cli_get_shows_priority(runner, vault_dir):
    set_priority(vault_dir, "DB", "critical")
    result = runner.invoke(priority_cmd, ["get", "DB", "--vault-dir", vault_dir])
    assert "critical" in result.output


def test_cli_list_shows_all(runner, vault_dir):
    set_priority(vault_dir, "A", "low")
    set_priority(vault_dir, "B", "high")
    result = runner.invoke(priority_cmd, ["list", "--vault-dir", vault_dir])
    assert "A: low" in result.output
    assert "B: high" in result.output


def test_cli_list_filter(runner, vault_dir):
    set_priority(vault_dir, "A", "low")
    set_priority(vault_dir, "B", "high")
    result = runner.invoke(priority_cmd, ["list", "--filter", "low", "--vault-dir", vault_dir])
    assert "A: low" in result.output
    assert "B" not in result.output
