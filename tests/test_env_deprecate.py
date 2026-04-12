"""Tests for env_vault.env_deprecate."""

import pytest

from env_vault.env_deprecate import (
    DeprecationInfo,
    deprecate_key,
    get_deprecation,
    is_deprecated,
    list_deprecated,
    undeprecate_key,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_deprecate_returns_true_when_new(vault_dir):
    assert deprecate_key(vault_dir, "OLD_KEY", "no longer used") is True


def test_deprecate_returns_false_when_updated(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", "no longer used")
    assert deprecate_key(vault_dir, "OLD_KEY", "updated reason") is False


def test_is_deprecated_true_after_deprecate(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", "reason")
    assert is_deprecated(vault_dir, "OLD_KEY") is True


def test_is_deprecated_false_before_deprecate(vault_dir):
    assert is_deprecated(vault_dir, "MISSING_KEY") is False


def test_get_deprecation_returns_info(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", "use new key", replacement="NEW_KEY")
    info = get_deprecation(vault_dir, "OLD_KEY")
    assert isinstance(info, DeprecationInfo)
    assert info.key == "OLD_KEY"
    assert info.reason == "use new key"
    assert info.replacement == "NEW_KEY"


def test_get_deprecation_missing_returns_none(vault_dir):
    assert get_deprecation(vault_dir, "GHOST") is None


def test_get_deprecation_no_replacement(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", "just old")
    info = get_deprecation(vault_dir, "OLD_KEY")
    assert info.replacement is None


def test_deprecation_info_str_with_replacement(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", "renamed", replacement="NEW_KEY")
    info = get_deprecation(vault_dir, "OLD_KEY")
    assert "OLD_KEY" in str(info)
    assert "renamed" in str(info)
    assert "NEW_KEY" in str(info)


def test_deprecation_info_str_without_replacement(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", "just old")
    info = get_deprecation(vault_dir, "OLD_KEY")
    result = str(info)
    assert "OLD_KEY" in result
    assert "just old" in result
    assert "instead" not in result


def test_undeprecate_returns_true_when_found(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", "reason")
    assert undeprecate_key(vault_dir, "OLD_KEY") is True


def test_undeprecate_returns_false_when_missing(vault_dir):
    assert undeprecate_key(vault_dir, "GHOST") is False


def test_undeprecate_removes_key(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", "reason")
    undeprecate_key(vault_dir, "OLD_KEY")
    assert is_deprecated(vault_dir, "OLD_KEY") is False


def test_list_deprecated_sorted(vault_dir):
    deprecate_key(vault_dir, "Z_KEY", "z")
    deprecate_key(vault_dir, "A_KEY", "a")
    deprecate_key(vault_dir, "M_KEY", "m")
    keys = [i.key for i in list_deprecated(vault_dir)]
    assert keys == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_deprecated_empty(vault_dir):
    assert list_deprecated(vault_dir) == []


def test_list_deprecated_excludes_undeprecated(vault_dir):
    deprecate_key(vault_dir, "A", "a")
    deprecate_key(vault_dir, "B", "b")
    undeprecate_key(vault_dir, "A")
    result = list_deprecated(vault_dir)
    assert len(result) == 1
    assert result[0].key == "B"
