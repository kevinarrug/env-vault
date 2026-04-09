"""Tests for env_vault.export module."""

from __future__ import annotations

import json

import pytest

from env_vault.export import (
    export_dotenv,
    export_json,
    export_shell,
    format_output,
    import_dotenv,
    import_json,
)


SAMPLE = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "s3cr3t"}


def test_export_dotenv_contains_all_keys():
    out = export_dotenv(SAMPLE)
    assert 'DATABASE_URL="postgres://localhost/db"' in out
    assert 'SECRET_KEY="s3cr3t"' in out


def test_export_dotenv_escapes_double_quotes():
    out = export_dotenv({"MSG": 'say "hello"'})
    assert 'MSG="say \\"hello\\""' in out


def test_export_json_valid_json():
    out = export_json(SAMPLE)
    parsed = json.loads(out)
    assert parsed == SAMPLE


def test_export_json_sorted_keys():
    out = export_json({"Z": "last", "A": "first"})
    assert out.index('"A"') < out.index('"Z"')


def test_export_shell_uses_export():
    out = export_shell(SAMPLE)
    assert "export DATABASE_URL=" in out
    assert "export SECRET_KEY=" in out


def test_export_shell_escapes_single_quotes():
    out = export_shell({"VAR": "it's fine"})
    assert "export VAR=" in out
    assert "it" in out


def test_import_dotenv_basic():
    content = 'FOO="bar"\nBAZ=qux\n'
    result = import_dotenv(content)
    assert result["FOO"] == "bar"
    assert result["BAZ"] == "qux"


def test_import_dotenv_ignores_comments():
    content = "# comment\nKEY=value\n"
    result = import_dotenv(content)
    assert "# comment" not in result
    assert result["KEY"] == "value"


def test_import_dotenv_single_quoted_values():
    result = import_dotenv("VAR='hello world'")
    assert result["VAR"] == "hello world"


def test_import_json_basic():
    content = json.dumps({"A": "1", "B": "2"})
    result = import_json(content)
    assert result == {"A": "1", "B": "2"}


def test_import_json_non_dict_raises():
    with pytest.raises(ValueError):
        import_json(json.dumps(["not", "a", "dict"]))


def test_format_output_dispatches_correctly():
    assert format_output(SAMPLE, "json") == export_json(SAMPLE)
    assert format_output(SAMPLE, "dotenv") == export_dotenv(SAMPLE)
    assert format_output(SAMPLE, "shell") == export_shell(SAMPLE)


def test_format_output_unknown_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        format_output(SAMPLE, "yaml")
