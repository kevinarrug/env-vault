"""Tests for env_vault.env_default."""
import pytest

from env_vault.env_default import (
    ResolveDefault,
    get_default,
    list_defaults,
    remove_default,
    resolve_with_default,
    set_default,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_default_returns_true_when_new(vault_dir):
    assert set_default(vault_dir, "DB_HOST", "localhost") is True


def test_set_default_returns_false_when_updated(vault_dir):
    set_default(vault_dir, "DB_HOST", "localhost")
    assert set_default(vault_dir, "DB_HOST", "remotehost") is False


def test_get_default_returns_value(vault_dir):
    set_default(vault_dir, "PORT", "5432")
    assert get_default(vault_dir, "PORT") == "5432"


def test_get_default_missing_returns_none(vault_dir):
    assert get_default(vault_dir, "MISSING") is None


def test_remove_default_returns_true_when_found(vault_dir):
    set_default(vault_dir, "KEY", "val")
    assert remove_default(vault_dir, "KEY") is True


def test_remove_default_returns_false_when_missing(vault_dir):
    assert remove_default(vault_dir, "GHOST") is False


def test_remove_default_actually_removes(vault_dir):
    set_default(vault_dir, "KEY", "val")
    remove_default(vault_dir, "KEY")
    assert get_default(vault_dir, "KEY") is None


def test_list_defaults_empty(vault_dir):
    assert list_defaults(vault_dir) == {}


def test_list_defaults_returns_all(vault_dir):
    set_default(vault_dir, "A", "1")
    set_default(vault_dir, "B", "2")
    result = list_defaults(vault_dir)
    assert result == {"A": "1", "B": "2"}


def test_resolve_prefers_vault_value(vault_dir):
    set_default(vault_dir, "HOST", "default-host")
    r = resolve_with_default(vault_dir, "HOST", "vault-host")
    assert r.value == "vault-host"
    assert r.from_default is False


def test_resolve_falls_back_to_default(vault_dir):
    set_default(vault_dir, "HOST", "default-host")
    r = resolve_with_default(vault_dir, "HOST", None)
    assert r.value == "default-host"
    assert r.from_default is True


def test_resolve_raises_when_no_value_or_default(vault_dir):
    with pytest.raises(KeyError, match="HOST"):
        resolve_with_default(vault_dir, "HOST", None)


def test_resolve_default_str_vault_source(vault_dir):
    r = ResolveDefault(key="X", value="hello", from_default=False)
    assert "vault" in str(r)
    assert "X" in str(r)


def test_resolve_default_str_default_source(vault_dir):
    r = ResolveDefault(key="X", value="hello", from_default=True)
    assert "default" in str(r)
