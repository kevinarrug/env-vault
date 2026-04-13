"""Tests for env_vault.env_trigger."""
import pytest

from env_vault.env_trigger import (
    add_trigger,
    clear_triggers,
    get_triggers,
    list_all_triggers,
    remove_trigger,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_add_trigger_returns_true_when_new(vault_dir):
    assert add_trigger(vault_dir, "DB_URL", "echo changed") is True


def test_add_trigger_returns_false_when_duplicate(vault_dir):
    add_trigger(vault_dir, "DB_URL", "echo changed")
    assert add_trigger(vault_dir, "DB_URL", "echo changed") is False


def test_get_triggers_returns_commands(vault_dir):
    add_trigger(vault_dir, "API_KEY", "curl http://hook")
    add_trigger(vault_dir, "API_KEY", "notify-send updated")
    cmds = get_triggers(vault_dir, "API_KEY")
    assert "curl http://hook" in cmds
    assert "notify-send updated" in cmds


def test_get_triggers_missing_key_returns_empty(vault_dir):
    assert get_triggers(vault_dir, "MISSING") == []


def test_remove_trigger_returns_true_when_found(vault_dir):
    add_trigger(vault_dir, "SECRET", "restart app")
    assert remove_trigger(vault_dir, "SECRET", "restart app") is True


def test_remove_trigger_returns_false_when_not_found(vault_dir):
    assert remove_trigger(vault_dir, "SECRET", "restart app") is False


def test_remove_trigger_cleans_up_empty_key(vault_dir):
    add_trigger(vault_dir, "SECRET", "restart app")
    remove_trigger(vault_dir, "SECRET", "restart app")
    assert "SECRET" not in list_all_triggers(vault_dir)


def test_list_all_triggers_returns_all_keys(vault_dir):
    add_trigger(vault_dir, "A", "cmd1")
    add_trigger(vault_dir, "B", "cmd2")
    mapping = list_all_triggers(vault_dir)
    assert "A" in mapping
    assert "B" in mapping


def test_clear_triggers_returns_count(vault_dir):
    add_trigger(vault_dir, "X", "cmd1")
    add_trigger(vault_dir, "X", "cmd2")
    assert clear_triggers(vault_dir, "X") == 2


def test_clear_triggers_removes_all(vault_dir):
    add_trigger(vault_dir, "X", "cmd1")
    clear_triggers(vault_dir, "X")
    assert get_triggers(vault_dir, "X") == []


def test_clear_triggers_missing_key_returns_zero(vault_dir):
    assert clear_triggers(vault_dir, "NOPE") == 0


def test_multiple_triggers_per_key_preserved(vault_dir):
    add_trigger(vault_dir, "K", "a")
    add_trigger(vault_dir, "K", "b")
    add_trigger(vault_dir, "K", "c")
    assert len(get_triggers(vault_dir, "K")) == 3
