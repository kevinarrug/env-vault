"""Tests for env_vault.env_type."""
import pytest

from env_vault.env_type import (
    VALID_TYPES,
    get_type,
    list_types,
    remove_type,
    set_type,
    validate_value,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_type_returns_true_when_new(vault_dir):
    assert set_type(vault_dir, "PORT", "int") is True


def test_set_type_returns_false_when_unchanged(vault_dir):
    set_type(vault_dir, "PORT", "int")
    assert set_type(vault_dir, "PORT", "int") is False


def test_set_type_returns_true_when_changed(vault_dir):
    set_type(vault_dir, "PORT", "int")
    assert set_type(vault_dir, "PORT", "string") is True


def test_get_type_returns_value(vault_dir):
    set_type(vault_dir, "DEBUG", "bool")
    assert get_type(vault_dir, "DEBUG") == "bool"


def test_get_type_missing_returns_none(vault_dir):
    assert get_type(vault_dir, "MISSING") is None


def test_remove_type_returns_true_when_found(vault_dir):
    set_type(vault_dir, "FOO", "string")
    assert remove_type(vault_dir, "FOO") is True


def test_remove_type_returns_false_when_missing(vault_dir):
    assert remove_type(vault_dir, "GHOST") is False


def test_remove_type_clears_entry(vault_dir):
    set_type(vault_dir, "FOO", "float")
    remove_type(vault_dir, "FOO")
    assert get_type(vault_dir, "FOO") is None


def test_list_types_returns_all(vault_dir):
    set_type(vault_dir, "A", "int")
    set_type(vault_dir, "B", "bool")
    result = list_types(vault_dir)
    assert result == {"A": "int", "B": "bool"}


def test_list_types_empty(vault_dir):
    assert list_types(vault_dir) == {}


def test_set_type_invalid_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid type"):
        set_type(vault_dir, "KEY", "datetime")


def test_valid_types_set_contains_expected():
    assert {"string", "int", "float", "bool", "json"} == VALID_TYPES


@pytest.mark.parametrize("value,type_name,expected", [
    ("hello", "string", True),
    ("42", "int", True),
    ("3.14", "float", True),
    ("true", "bool", True),
    ("yes", "bool", True),
    ('{"k": 1}', "json", True),
    ("abc", "int", False),
    ("abc", "float", False),
    ("maybe", "bool", False),
    ("not-json", "json", False),
])
def test_validate_value(value, type_name, expected):
    assert validate_value(value, type_name) is expected
