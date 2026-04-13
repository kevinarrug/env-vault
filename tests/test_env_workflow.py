"""Tests for env_vault.env_workflow."""
import pytest
from env_vault.env_workflow import (
    set_step,
    get_step,
    remove_step,
    list_steps,
    keys_in_step,
    VALID_STEPS,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_step_returns_true_when_new(vault_dir):
    assert set_step(vault_dir, "API_KEY", "draft") is True


def test_set_step_returns_false_when_unchanged(vault_dir):
    set_step(vault_dir, "API_KEY", "draft")
    assert set_step(vault_dir, "API_KEY", "draft") is False


def test_set_step_returns_true_when_changed(vault_dir):
    set_step(vault_dir, "API_KEY", "draft")
    assert set_step(vault_dir, "API_KEY", "review") is True


def test_get_step_returns_value(vault_dir):
    set_step(vault_dir, "DB_PASS", "approved")
    assert get_step(vault_dir, "DB_PASS") == "approved"


def test_get_step_missing_returns_none(vault_dir):
    assert get_step(vault_dir, "MISSING_KEY") is None


def test_set_invalid_step_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid step"):
        set_step(vault_dir, "API_KEY", "unknown_step")


def test_remove_step_returns_true_when_found(vault_dir):
    set_step(vault_dir, "API_KEY", "draft")
    assert remove_step(vault_dir, "API_KEY") is True


def test_remove_step_returns_false_when_missing(vault_dir):
    assert remove_step(vault_dir, "MISSING_KEY") is False


def test_remove_step_clears_value(vault_dir):
    set_step(vault_dir, "API_KEY", "draft")
    remove_step(vault_dir, "API_KEY")
    assert get_step(vault_dir, "API_KEY") is None


def test_list_steps_returns_all(vault_dir):
    set_step(vault_dir, "KEY_A", "draft")
    set_step(vault_dir, "KEY_B", "approved")
    result = list_steps(vault_dir)
    assert result == {"KEY_A": "draft", "KEY_B": "approved"}


def test_list_steps_empty_when_none(vault_dir):
    assert list_steps(vault_dir) == {}


def test_keys_in_step_returns_matching_keys(vault_dir):
    set_step(vault_dir, "KEY_A", "review")
    set_step(vault_dir, "KEY_B", "draft")
    set_step(vault_dir, "KEY_C", "review")
    result = keys_in_step(vault_dir, "review")
    assert result == ["KEY_A", "KEY_C"]


def test_keys_in_step_empty_when_none_match(vault_dir):
    set_step(vault_dir, "KEY_A", "draft")
    assert keys_in_step(vault_dir, "approved") == []


def test_keys_in_step_invalid_step_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid step"):
        keys_in_step(vault_dir, "nonexistent")


def test_valid_steps_contains_expected_values():
    assert "draft" in VALID_STEPS
    assert "approved" in VALID_STEPS
    assert "archived" in VALID_STEPS
