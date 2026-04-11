"""Tests for env_vault.env_transform."""
from __future__ import annotations

import pytest

from env_vault.env_transform import (
    TransformResult,
    apply_pipeline,
    list_transforms,
    transform_and_save,
    transform_key,
)
from env_vault.vault import Vault


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path))
    v.set("API_KEY", "hello world", "pass")
    v.set("SECRET", "AbCdEf", "pass")
    return v


# --- apply_pipeline ---

def test_apply_pipeline_upper():
    result, err = apply_pipeline("hello", ["upper"])
    assert result == "HELLO"
    assert err is None


def test_apply_pipeline_lower():
    result, err = apply_pipeline("HELLO", ["lower"])
    assert result == "hello"
    assert err is None


def test_apply_pipeline_strip():
    result, err = apply_pipeline("  hi  ", ["strip"])
    assert result == "hi"
    assert err is None


def test_apply_pipeline_chained():
    result, err = apply_pipeline("  Hello  ", ["strip", "upper"])
    assert result == "HELLO"
    assert err is None


def test_apply_pipeline_reverse():
    result, err = apply_pipeline("abc", ["reverse"])
    assert result == "cba"
    assert err is None


def test_apply_pipeline_base64_roundtrip():
    original = "my-secret"
    encoded, _ = apply_pipeline(original, ["base64_encode"])
    decoded, err = apply_pipeline(encoded, ["base64_decode"])
    assert decoded == original
    assert err is None


def test_apply_pipeline_unknown_step_returns_error():
    result, err = apply_pipeline("value", ["nonexistent"])
    assert err is not None
    assert "unknown transform" in err


def test_apply_pipeline_empty_returns_unchanged():
    result, err = apply_pipeline("value", [])
    assert result == "value"
    assert err is None


# --- TransformResult ---

def test_transform_result_ok_true_when_no_error():
    r = TransformResult(key="K", original="a", transformed="A", pipeline=["upper"])
    assert r.ok is True


def test_transform_result_ok_false_when_error():
    r = TransformResult(key="K", original="a", transformed="a", pipeline=[], error="oops")
    assert r.ok is False


def test_transform_result_str_contains_key():
    r = TransformResult(key="MY_KEY", original="a", transformed="A", pipeline=["upper"])
    assert "MY_KEY" in str(r)


def test_transform_result_str_contains_error():
    r = TransformResult(key="K", original="a", transformed="a", pipeline=[], error="bad step")
    assert "bad step" in str(r)


# --- transform_key / transform_and_save ---

def test_transform_key_returns_result(vault, tmp_path):
    result = transform_key(vault, "pass", "API_KEY", ["upper"])
    assert isinstance(result, TransformResult)
    assert result.transformed == "HELLO WORLD"
    assert result.ok


def test_transform_key_does_not_modify_vault(vault, tmp_path):
    transform_key(vault, "pass", "API_KEY", ["upper"])
    assert vault.get("API_KEY", "pass") == "hello world"


def test_transform_and_save_persists_value(vault, tmp_path):
    result = transform_and_save(vault, "pass", "SECRET", ["lower"])
    assert result.ok
    assert vault.get("SECRET", "pass") == "abcdef"


def test_transform_and_save_unknown_step_does_not_save(vault):
    original = vault.get("API_KEY", "pass")
    result = transform_and_save(vault, "pass", "API_KEY", ["bad_step"])
    assert not result.ok
    assert vault.get("API_KEY", "pass") == original


# --- list_transforms ---

def test_list_transforms_returns_sorted_list():
    names = list_transforms()
    assert names == sorted(names)


def test_list_transforms_includes_expected():
    names = list_transforms()
    for expected in ("upper", "lower", "strip", "reverse", "base64_encode"):
        assert expected in names
