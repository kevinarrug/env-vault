"""Tests for env_vault.env_import_map."""
from __future__ import annotations

import pytest

from env_vault.env_import_map import (
    MapResult,
    apply_map,
    get_mappings,
    remove_mapping,
    set_mapping,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


# --- set_mapping / get_mappings ---

def test_set_mapping_returns_true_when_new(vault_dir):
    assert set_mapping(vault_dir, "OLD_KEY", "NEW_KEY") is True


def test_set_mapping_returns_false_when_updated(vault_dir):
    set_mapping(vault_dir, "OLD_KEY", "NEW_KEY")
    assert set_mapping(vault_dir, "OLD_KEY", "OTHER_KEY") is False


def test_get_mappings_returns_all(vault_dir):
    set_mapping(vault_dir, "A", "AA")
    set_mapping(vault_dir, "B", "BB")
    result = get_mappings(vault_dir)
    assert result == {"A": "AA", "B": "BB"}


def test_get_mappings_empty_when_none(vault_dir):
    assert get_mappings(vault_dir) == {}


# --- remove_mapping ---

def test_remove_mapping_returns_true_when_found(vault_dir):
    set_mapping(vault_dir, "X", "Y")
    assert remove_mapping(vault_dir, "X") is True


def test_remove_mapping_returns_false_when_missing(vault_dir):
    assert remove_mapping(vault_dir, "GHOST") is False


def test_remove_mapping_actually_removes(vault_dir):
    set_mapping(vault_dir, "X", "Y")
    remove_mapping(vault_dir, "X")
    assert "X" not in get_mappings(vault_dir)


# --- apply_map ---

def test_apply_map_remaps_known_key(vault_dir):
    set_mapping(vault_dir, "DB_HOST", "DATABASE_HOST")
    data = {"DB_HOST": "localhost"}
    remapped, report = apply_map(vault_dir, data)
    assert "DATABASE_HOST" in remapped
    assert remapped["DATABASE_HOST"] == "localhost"
    assert report.applied == {"DB_HOST": "DATABASE_HOST"}


def test_apply_map_passes_through_unknown_key(vault_dir):
    data = {"UNKNOWN": "value"}
    remapped, report = apply_map(vault_dir, data)
    assert remapped["UNKNOWN"] == "value"
    assert "UNKNOWN" in report.skipped


def test_apply_map_strict_skips_unmapped(vault_dir):
    data = {"UNKNOWN": "value"}
    remapped, report = apply_map(vault_dir, data, strict=True)
    assert "UNKNOWN" not in remapped
    assert report.warnings


def test_apply_map_collision_produces_warning(vault_dir):
    set_mapping(vault_dir, "A", "C")
    set_mapping(vault_dir, "B", "C")
    data = {"A": "first", "B": "second"}
    remapped, report = apply_map(vault_dir, data)
    # One of them wins; the other triggers a warning
    assert "C" in remapped
    assert report.warnings


# --- MapResult ---

def test_map_result_has_remaps_false_when_empty():
    r = MapResult()
    assert r.has_remaps is False


def test_map_result_has_remaps_true_when_applied():
    r = MapResult(applied={"OLD": "NEW"})
    assert r.has_remaps is True


def test_map_result_summary_no_changes():
    r = MapResult()
    assert r.summary() == "no changes"


def test_map_result_summary_counts(vault_dir):
    set_mapping(vault_dir, "K", "V")
    data = {"K": "val", "OTHER": "x"}
    _, report = apply_map(vault_dir, data)
    summary = report.summary()
    assert "1 key(s) remapped" in summary
    assert "1 key(s) passed through" in summary
