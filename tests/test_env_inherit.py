"""Tests for env_vault.env_inherit."""
import pytest

from env_vault.vault import Vault
from env_vault.env_inherit import (
    InheritResult,
    InheritReport,
    resolve_inherited,
    apply_inheritance,
)

PASS = "testpass"


@pytest.fixture()
def vault_pair(tmp_path):
    parent_dir = tmp_path / "parent"
    child_dir = tmp_path / "child"
    parent = Vault(str(parent_dir))
    child = Vault(str(child_dir))

    parent.set("SHARED", "from_parent", PASS)
    parent.set("PARENT_ONLY", "parent_val", PASS)

    child.set("SHARED", "from_child", PASS)
    child.set("CHILD_ONLY", "child_val", PASS)

    return child, parent


def test_resolve_returns_all_keys(vault_pair):
    child, parent = vault_pair
    report = resolve_inherited(child, parent, PASS)
    keys = {e.key for e in report.entries}
    assert keys == {"SHARED", "PARENT_ONLY", "CHILD_ONLY"}


def test_resolve_child_wins_for_shared_key(vault_pair):
    child, parent = vault_pair
    report = resolve_inherited(child, parent, PASS)
    shared = next(e for e in report.entries if e.key == "SHARED")
    assert shared.value == "from_child"
    assert shared.source == "child"
    assert shared.overridden is True


def test_resolve_parent_only_key_comes_from_parent(vault_pair):
    child, parent = vault_pair
    report = resolve_inherited(child, parent, PASS)
    entry = next(e for e in report.entries if e.key == "PARENT_ONLY")
    assert entry.value == "parent_val"
    assert entry.source == "parent"
    assert entry.overridden is False


def test_resolve_child_only_key_comes_from_child(vault_pair):
    child, parent = vault_pair
    report = resolve_inherited(child, parent, PASS)
    entry = next(e for e in report.entries if e.key == "CHILD_ONLY")
    assert entry.source == "child"


def test_report_inherited_keys(vault_pair):
    child, parent = vault_pair
    report = resolve_inherited(child, parent, PASS)
    assert "PARENT_ONLY" in report.inherited_keys
    assert "SHARED" not in report.inherited_keys


def test_report_overridden_keys(vault_pair):
    child, parent = vault_pair
    report = resolve_inherited(child, parent, PASS)
    assert "SHARED" in report.overridden_keys


def test_summary_format(vault_pair):
    child, parent = vault_pair
    report = resolve_inherited(child, parent, PASS)
    s = report.summary()
    assert "inherited" in s
    assert "overridden" in s


def test_apply_inheritance_copies_missing_keys(vault_pair):
    child, parent = vault_pair
    written = apply_inheritance(child, parent, PASS)
    assert "PARENT_ONLY" in written
    assert child.get("PARENT_ONLY", PASS) == "parent_val"


def test_apply_inheritance_does_not_overwrite_by_default(vault_pair):
    child, parent = vault_pair
    apply_inheritance(child, parent, PASS)
    assert child.get("SHARED", PASS) == "from_child"


def test_apply_inheritance_overwrites_when_flag_set(vault_pair):
    child, parent = vault_pair
    apply_inheritance(child, parent, PASS, overwrite=True)
    assert child.get("SHARED", PASS) == "from_parent"


def test_inherit_result_str(vault_pair):
    entry = InheritResult(key="FOO", value="bar", source="parent", overridden=False)
    assert "FOO" in str(entry)
    assert "parent" in str(entry)
