"""Tests for env_vault.env_depends."""
import pytest
from pathlib import Path
from env_vault.env_depends import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    resolve_order,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_add_dependency_returns_true_when_new(vault_dir):
    assert add_dependency(vault_dir, "B", "A") is True


def test_add_dependency_returns_false_when_duplicate(vault_dir):
    add_dependency(vault_dir, "B", "A")
    assert add_dependency(vault_dir, "B", "A") is False


def test_get_dependencies_returns_list(vault_dir):
    add_dependency(vault_dir, "B", "A")
    add_dependency(vault_dir, "B", "C")
    deps = get_dependencies(vault_dir, "B")
    assert set(deps) == {"A", "C"}


def test_get_dependencies_missing_key_returns_empty(vault_dir):
    assert get_dependencies(vault_dir, "NONEXISTENT") == []


def test_get_dependents_returns_keys_that_depend_on_target(vault_dir):
    add_dependency(vault_dir, "B", "A")
    add_dependency(vault_dir, "C", "A")
    dependents = get_dependents(vault_dir, "A")
    assert set(dependents) == {"B", "C"}


def test_get_dependents_empty_when_none(vault_dir):
    assert get_dependents(vault_dir, "A") == []


def test_remove_dependency_returns_true_when_found(vault_dir):
    add_dependency(vault_dir, "B", "A")
    assert remove_dependency(vault_dir, "B", "A") is True


def test_remove_dependency_returns_false_when_missing(vault_dir):
    assert remove_dependency(vault_dir, "B", "A") is False


def test_remove_dependency_cleans_up_empty_key(vault_dir):
    add_dependency(vault_dir, "B", "A")
    remove_dependency(vault_dir, "B", "A")
    assert get_dependencies(vault_dir, "B") == []


def test_resolve_order_simple_chain(vault_dir):
    add_dependency(vault_dir, "C", "B")
    add_dependency(vault_dir, "B", "A")
    order = resolve_order(vault_dir, ["A", "B", "C"])
    assert order.index("A") < order.index("B") < order.index("C")


def test_resolve_order_no_deps_returns_all_keys(vault_dir):
    order = resolve_order(vault_dir, ["X", "Y", "Z"])
    assert set(order) == {"X", "Y", "Z"}


def test_resolve_order_cycle_raises(vault_dir):
    add_dependency(vault_dir, "A", "B")
    add_dependency(vault_dir, "B", "A")
    with pytest.raises(ValueError, match="cycle"):
        resolve_order(vault_dir, ["A", "B"])


def test_resolve_order_all_keys_when_none_specified(vault_dir):
    add_dependency(vault_dir, "B", "A")
    order = resolve_order(vault_dir)
    assert order.index("A") < order.index("B")
