import pytest
from pathlib import Path
from env_vault.env_badge import (
    set_badge,
    remove_badge,
    get_badge,
    list_badges,
    filter_by_badge,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_badge_returns_true_when_new(vault_dir):
    assert set_badge(vault_dir, "API_KEY", "stable") is True


def test_set_badge_returns_false_when_unchanged(vault_dir):
    set_badge(vault_dir, "API_KEY", "stable")
    assert set_badge(vault_dir, "API_KEY", "stable") is False


def test_set_badge_returns_true_when_changed(vault_dir):
    set_badge(vault_dir, "API_KEY", "stable")
    assert set_badge(vault_dir, "API_KEY", "beta") is True


def test_get_badge_returns_value(vault_dir):
    set_badge(vault_dir, "API_KEY", "experimental")
    assert get_badge(vault_dir, "API_KEY") == "experimental"


def test_get_badge_missing_returns_none(vault_dir):
    assert get_badge(vault_dir, "MISSING") is None


def test_remove_badge_returns_true_when_found(vault_dir):
    set_badge(vault_dir, "API_KEY", "stable")
    assert remove_badge(vault_dir, "API_KEY") is True


def test_remove_badge_returns_false_when_missing(vault_dir):
    assert remove_badge(vault_dir, "GHOST") is False


def test_remove_badge_clears_entry(vault_dir):
    set_badge(vault_dir, "API_KEY", "stable")
    remove_badge(vault_dir, "API_KEY")
    assert get_badge(vault_dir, "API_KEY") is None


def test_list_badges_returns_all(vault_dir):
    set_badge(vault_dir, "A", "stable")
    set_badge(vault_dir, "B", "beta")
    result = list_badges(vault_dir)
    assert result == {"A": "stable", "B": "beta"}


def test_list_badges_empty(vault_dir):
    assert list_badges(vault_dir) == {}


def test_filter_by_badge_returns_matching_keys(vault_dir):
    set_badge(vault_dir, "A", "stable")
    set_badge(vault_dir, "B", "beta")
    set_badge(vault_dir, "C", "stable")
    result = filter_by_badge(vault_dir, "stable")
    assert sorted(result) == ["A", "C"]


def test_filter_by_badge_no_matches(vault_dir):
    set_badge(vault_dir, "A", "stable")
    assert filter_by_badge(vault_dir, "internal") == []


def test_set_badge_invalid_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid badge"):
        set_badge(vault_dir, "KEY", "unknown")


def test_badge_file_created(vault_dir):
    set_badge(vault_dir, "X", "public")
    assert Path(vault_dir, ".env_badge.json").exists()
