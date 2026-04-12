"""Tests for env_vault.env_ref."""
import pytest

from env_vault.env_ref import (
    set_ref,
    remove_ref,
    get_ref,
    list_refs,
    resolve_ref,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# set_ref
# ---------------------------------------------------------------------------

def test_set_ref_returns_true_when_new(vault_dir):
    assert set_ref(vault_dir, "DB_URL", "DATABASE_URL") is True


def test_set_ref_returns_false_when_updated(vault_dir):
    set_ref(vault_dir, "DB_URL", "DATABASE_URL")
    assert set_ref(vault_dir, "DB_URL", "POSTGRES_URL") is False


def test_set_ref_self_reference_raises(vault_dir):
    with pytest.raises(ValueError, match="cannot reference itself"):
        set_ref(vault_dir, "KEY", "KEY")


# ---------------------------------------------------------------------------
# get_ref
# ---------------------------------------------------------------------------

def test_get_ref_returns_target(vault_dir):
    set_ref(vault_dir, "DB_URL", "DATABASE_URL")
    assert get_ref(vault_dir, "DB_URL") == "DATABASE_URL"


def test_get_ref_missing_returns_none(vault_dir):
    assert get_ref(vault_dir, "MISSING") is None


# ---------------------------------------------------------------------------
# remove_ref
# ---------------------------------------------------------------------------

def test_remove_ref_returns_true_when_found(vault_dir):
    set_ref(vault_dir, "DB_URL", "DATABASE_URL")
    assert remove_ref(vault_dir, "DB_URL") is True


def test_remove_ref_returns_false_when_missing(vault_dir):
    assert remove_ref(vault_dir, "NOPE") is False


def test_remove_ref_clears_entry(vault_dir):
    set_ref(vault_dir, "DB_URL", "DATABASE_URL")
    remove_ref(vault_dir, "DB_URL")
    assert get_ref(vault_dir, "DB_URL") is None


# ---------------------------------------------------------------------------
# list_refs
# ---------------------------------------------------------------------------

def test_list_refs_empty(vault_dir):
    assert list_refs(vault_dir) == {}


def test_list_refs_returns_all(vault_dir):
    set_ref(vault_dir, "A", "B")
    set_ref(vault_dir, "C", "D")
    assert list_refs(vault_dir) == {"A": "B", "C": "D"}


# ---------------------------------------------------------------------------
# resolve_ref
# ---------------------------------------------------------------------------

class _FakeVault:
    def __init__(self, data: dict):
        self._data = data

    def get(self, key: str) -> str:
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]


def test_resolve_direct_value(vault_dir):
    vault = _FakeVault({"DATABASE_URL": "postgres://localhost/db"})
    # No ref set — reads directly
    assert resolve_ref(vault_dir, "DATABASE_URL", vault) == "postgres://localhost/db"


def test_resolve_follows_reference(vault_dir):
    set_ref(vault_dir, "DB_URL", "DATABASE_URL")
    vault = _FakeVault({"DATABASE_URL": "postgres://localhost/db"})
    assert resolve_ref(vault_dir, "DB_URL", vault) == "postgres://localhost/db"


def test_resolve_chained_references(vault_dir):
    set_ref(vault_dir, "A", "B")
    set_ref(vault_dir, "B", "C")
    vault = _FakeVault({"C": "final_value"})
    assert resolve_ref(vault_dir, "A", vault) == "final_value"


def test_resolve_missing_key_returns_none(vault_dir):
    vault = _FakeVault({})
    assert resolve_ref(vault_dir, "MISSING", vault) is None


def test_resolve_circular_reference_returns_none(vault_dir):
    set_ref(vault_dir, "A", "B")
    set_ref(vault_dir, "B", "A")
    vault = _FakeVault({})
    assert resolve_ref(vault_dir, "A", vault) is None
