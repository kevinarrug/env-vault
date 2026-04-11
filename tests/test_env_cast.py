"""Tests for env_vault.env_cast."""

from __future__ import annotations

import pytest

from env_vault.env_cast import cast_value, cast_key, cast_all, cast_to_dict, CastResult


# ---------------------------------------------------------------------------
# cast_value unit tests
# ---------------------------------------------------------------------------

def test_cast_str_returns_string():
    assert cast_value("hello", "str") == "hello"


def test_cast_int_valid():
    assert cast_value("42", "int") == 42


def test_cast_int_invalid_raises():
    with pytest.raises(ValueError):
        cast_value("not_a_number", "int")


def test_cast_float_valid():
    assert cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_bool_truthy_values():
    for val in ("1", "true", "yes", "on", "True", "YES"):
        assert cast_value(val, "bool") is True


def test_cast_bool_falsy_values():
    for val in ("0", "false", "no", "off", "False", "NO"):
        assert cast_value(val, "bool") is False


def test_cast_bool_invalid_raises():
    with pytest.raises(ValueError):
        cast_value("maybe", "bool")


def test_cast_list_splits_by_comma():
    assert cast_value("a, b, c", "list") == ["a", "b", "c"]


def test_cast_list_strips_whitespace():
    assert cast_value(" x , y ", "list") == ["x", "y"]


def test_cast_list_empty_string_returns_empty():
    assert cast_value("", "list") == []


def test_cast_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported cast type"):
        cast_value("val", "dict")


# ---------------------------------------------------------------------------
# cast_key / cast_all / cast_to_dict with a fake vault
# ---------------------------------------------------------------------------

class _FakeVault:
    def __init__(self, data):
        self._data = data

    def get(self, key, passphrase):
        return self._data[key]


@pytest.fixture
def fake_vault():
    return _FakeVault({"PORT": "8080", "DEBUG": "true", "RATE": "1.5", "TAGS": "a,b,c"})


def test_cast_key_success(fake_vault):
    result = cast_key(fake_vault, "PORT", "int", "pass")
    assert isinstance(result, CastResult)
    assert result.success is True
    assert result.value == 8080


def test_cast_key_failure_returns_result(fake_vault):
    result = cast_key(fake_vault, "TAGS", "int", "pass")
    assert result.success is False
    assert result.error is not None


def test_cast_all_returns_list(fake_vault):
    schema = {"PORT": "int", "DEBUG": "bool"}
    results = cast_all(fake_vault, schema, "pass")
    assert len(results) == 2
    assert all(isinstance(r, CastResult) for r in results)


def test_cast_to_dict_success(fake_vault):
    schema = {"PORT": "int", "RATE": "float", "DEBUG": "bool"}
    out = cast_to_dict(fake_vault, schema, "pass")
    assert out["PORT"] == 8080
    assert out["RATE"] == pytest.approx(1.5)
    assert out["DEBUG"] is True


def test_cast_to_dict_raises_on_failure(fake_vault):
    schema = {"TAGS": "int"}
    with pytest.raises(ValueError):
        cast_to_dict(fake_vault, schema, "pass")


def test_cast_result_str_success(fake_vault):
    result = cast_key(fake_vault, "PORT", "int", "pass")
    assert "PORT" in str(result)
    assert "int" in str(result)


def test_cast_result_str_failure(fake_vault):
    result = cast_key(fake_vault, "TAGS", "int", "pass")
    assert "cast error" in str(result)
