"""Tests for env_vault.diff module."""

import pytest

from env_vault.diff import DiffResult, diff_dicts, diff_vaults


# ---------------------------------------------------------------------------
# DiffResult helpers
# ---------------------------------------------------------------------------

def test_diff_result_has_changes_true():
    r = DiffResult(added=["FOO"])
    assert r.has_changes is True


def test_diff_result_has_changes_false():
    r = DiffResult(unchanged=["FOO"])
    assert r.has_changes is False


def test_diff_result_summary_no_changes():
    r = DiffResult(unchanged=["FOO"])
    assert r.summary() == "No changes."


def test_diff_result_summary_format():
    r = DiffResult(added=["NEW"], removed=["OLD"], changed=["MOD"])
    summary = r.summary()
    assert "+ NEW" in summary
    assert "- OLD" in summary
    assert "~ MOD" in summary


# ---------------------------------------------------------------------------
# diff_dicts
# ---------------------------------------------------------------------------

def test_diff_dicts_added():
    result = diff_dicts({"A": "1"}, {"A": "1", "B": "2"})
    assert result.added == ["B"]
    assert result.removed == []
    assert result.changed == []


def test_diff_dicts_removed():
    result = diff_dicts({"A": "1", "B": "2"}, {"A": "1"})
    assert result.removed == ["B"]
    assert result.added == []


def test_diff_dicts_changed():
    result = diff_dicts({"A": "old"}, {"A": "new"})
    assert result.changed == ["A"]
    assert result.unchanged == []


def test_diff_dicts_unchanged():
    result = diff_dicts({"A": "same"}, {"A": "same"})
    assert result.unchanged == ["A"]
    assert not result.has_changes


def test_diff_dicts_empty_both():
    result = diff_dicts({}, {})
    assert not result.has_changes


# ---------------------------------------------------------------------------
# diff_vaults  (uses real Vault objects)
# ---------------------------------------------------------------------------

@pytest.fixture()
def two_vaults(tmp_path):
    from env_vault.vault import Vault

    passphrase = "secret"
    dir_a = tmp_path / "vault_a"
    dir_b = tmp_path / "vault_b"
    dir_a.mkdir()
    dir_b.mkdir()

    va = Vault(str(dir_a))
    vb = Vault(str(dir_b))

    va.set("SHARED", "hello", passphrase)
    va.set("ONLY_A", "gone", passphrase)

    vb.set("SHARED", "hello", passphrase)
    vb.set("ONLY_B", "new", passphrase)
    vb.set("CHANGED", "v2", passphrase)
    va.set("CHANGED", "v1", passphrase)

    return va, vb, passphrase


def test_diff_vaults_added(two_vaults):
    va, vb, pw = two_vaults
    result = diff_vaults(va, vb, pw)
    assert "ONLY_B" in result.added


def test_diff_vaults_removed(two_vaults):
    va, vb, pw = two_vaults
    result = diff_vaults(va, vb, pw)
    assert "ONLY_A" in result.removed


def test_diff_vaults_changed(two_vaults):
    va, vb, pw = two_vaults
    result = diff_vaults(va, vb, pw)
    assert "CHANGED" in result.changed


def test_diff_vaults_unchanged(two_vaults):
    va, vb, pw = two_vaults
    result = diff_vaults(va, vb, pw)
    assert "SHARED" in result.unchanged
