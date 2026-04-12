"""Tests for env_vault.env_source."""
import pytest

from env_vault.env_source import (
    get_source,
    keys_by_source,
    list_sources,
    remove_source,
    set_source,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_source_returns_true_when_new(vault_dir):
    assert set_source(vault_dir, "DB_HOST", "terraform") is True


def test_set_source_returns_false_when_updated(vault_dir):
    set_source(vault_dir, "DB_HOST", "terraform")
    assert set_source(vault_dir, "DB_HOST", "ansible") is False


def test_get_source_returns_value(vault_dir):
    set_source(vault_dir, "API_KEY", "doppler")
    assert get_source(vault_dir, "API_KEY") == "doppler"


def test_get_source_missing_returns_none(vault_dir):
    assert get_source(vault_dir, "MISSING") is None


def test_remove_source_returns_true_when_found(vault_dir):
    set_source(vault_dir, "SECRET", "vault")
    assert remove_source(vault_dir, "SECRET") is True


def test_remove_source_returns_false_when_missing(vault_dir):
    assert remove_source(vault_dir, "GHOST") is False


def test_remove_source_deletes_entry(vault_dir):
    set_source(vault_dir, "TOKEN", "ci")
    remove_source(vault_dir, "TOKEN")
    assert get_source(vault_dir, "TOKEN") is None


def test_list_sources_returns_all(vault_dir):
    set_source(vault_dir, "A", "terraform")
    set_source(vault_dir, "B", "ansible")
    result = list_sources(vault_dir)
    assert result == {"A": "terraform", "B": "ansible"}


def test_list_sources_empty_when_none(vault_dir):
    assert list_sources(vault_dir) == {}


def test_keys_by_source_returns_matching_keys(vault_dir):
    set_source(vault_dir, "DB_HOST", "terraform")
    set_source(vault_dir, "DB_PASS", "terraform")
    set_source(vault_dir, "API_KEY", "doppler")
    result = keys_by_source(vault_dir, "terraform")
    assert result == ["DB_HOST", "DB_PASS"]


def test_keys_by_source_returns_empty_when_no_match(vault_dir):
    set_source(vault_dir, "X", "ansible")
    assert keys_by_source(vault_dir, "terraform") == []


def test_keys_by_source_returns_sorted(vault_dir):
    set_source(vault_dir, "Z_KEY", "ci")
    set_source(vault_dir, "A_KEY", "ci")
    set_source(vault_dir, "M_KEY", "ci")
    assert keys_by_source(vault_dir, "ci") == ["A_KEY", "M_KEY", "Z_KEY"]


def test_update_source_persists_new_value(vault_dir):
    set_source(vault_dir, "HOST", "terraform")
    set_source(vault_dir, "HOST", "pulumi")
    assert get_source(vault_dir, "HOST") == "pulumi"
