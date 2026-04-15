"""Tests for env_vault.env_rating."""

import pytest

from env_vault.env_rating import (
    average_rating,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_rating_returns_true_when_new(vault_dir):
    assert set_rating(vault_dir, "API_KEY", 4) is True


def test_set_rating_returns_false_when_unchanged(vault_dir):
    set_rating(vault_dir, "API_KEY", 3)
    assert set_rating(vault_dir, "API_KEY", 3) is False


def test_set_rating_returns_true_when_changed(vault_dir):
    set_rating(vault_dir, "API_KEY", 3)
    assert set_rating(vault_dir, "API_KEY", 5) is True


def test_get_rating_returns_value(vault_dir):
    set_rating(vault_dir, "DB_PASS", 2)
    assert get_rating(vault_dir, "DB_PASS") == 2


def test_get_rating_missing_returns_none(vault_dir):
    assert get_rating(vault_dir, "MISSING") is None


def test_set_rating_invalid_raises(vault_dir):
    with pytest.raises(ValueError, match="Rating must be 1-5"):
        set_rating(vault_dir, "KEY", 0)


def test_set_rating_too_high_raises(vault_dir):
    with pytest.raises(ValueError, match="Rating must be 1-5"):
        set_rating(vault_dir, "KEY", 6)


def test_remove_rating_returns_true_when_found(vault_dir):
    set_rating(vault_dir, "TOKEN", 5)
    assert remove_rating(vault_dir, "TOKEN") is True


def test_remove_rating_returns_false_when_missing(vault_dir):
    assert remove_rating(vault_dir, "GHOST") is False


def test_remove_rating_clears_value(vault_dir):
    set_rating(vault_dir, "TOKEN", 5)
    remove_rating(vault_dir, "TOKEN")
    assert get_rating(vault_dir, "TOKEN") is None


def test_list_ratings_returns_sorted(vault_dir):
    set_rating(vault_dir, "Z_KEY", 1)
    set_rating(vault_dir, "A_KEY", 5)
    result = list_ratings(vault_dir)
    assert list(result.keys()) == ["A_KEY", "Z_KEY"]


def test_list_ratings_empty(vault_dir):
    assert list_ratings(vault_dir) == {}


def test_average_rating_none_when_empty(vault_dir):
    assert average_rating(vault_dir) is None


def test_average_rating_single_key(vault_dir):
    set_rating(vault_dir, "KEY", 4)
    assert average_rating(vault_dir) == pytest.approx(4.0)


def test_average_rating_multiple_keys(vault_dir):
    set_rating(vault_dir, "A", 2)
    set_rating(vault_dir, "B", 4)
    assert average_rating(vault_dir) == pytest.approx(3.0)
