"""Tests for env_vault.merge."""

from __future__ import annotations

import pytest

from env_vault.merge import (
    ConflictStrategy,
    MergeConflict,
    MergeConflictError,
    MergeResult,
    merge_dicts,
)


# ---------------------------------------------------------------------------
# MergeResult helpers
# ---------------------------------------------------------------------------

def test_has_conflicts_false_when_empty():
    r = MergeResult(merged={}, added=[], updated=[], conflicts=[])
    assert r.has_conflicts is False


def test_has_conflicts_true_when_present():
    r = MergeResult(conflicts=[MergeConflict("K", "a", "b")])
    assert r.has_conflicts is True


def test_summary_no_changes():
    r = MergeResult(merged={"A": "1"})
    assert r.summary() == "no changes"


def test_summary_counts():
    r = MergeResult(
        added=["A"],
        updated=["B", "C"],
        conflicts=[MergeConflict("D", "x", "y")],
    )
    assert "1 added" in r.summary()
    assert "2 updated" in r.summary()
    assert "1 conflict" in r.summary()


# ---------------------------------------------------------------------------
# merge_dicts — additions
# ---------------------------------------------------------------------------

def test_merge_adds_new_keys():
    result = merge_dicts({"A": "1"}, {"B": "2"})
    assert result.merged == {"A": "1", "B": "2"}
    assert "B" in result.added


def test_merge_identical_values_no_conflict():
    result = merge_dicts({"A": "1"}, {"A": "1"})
    assert result.has_conflicts is False
    assert result.merged == {"A": "1"}


# ---------------------------------------------------------------------------
# merge_dicts — conflict strategies
# ---------------------------------------------------------------------------

def test_merge_conflict_strategy_ours_keeps_base():
    result = merge_dicts({"A": "base"}, {"A": "other"}, strategy=ConflictStrategy.OURS)
    assert result.merged["A"] == "base"
    assert result.has_conflicts is True
    assert "A" not in result.updated


def test_merge_conflict_strategy_theirs_takes_other():
    result = merge_dicts({"A": "base"}, {"A": "other"}, strategy=ConflictStrategy.THEIRS)
    assert result.merged["A"] == "other"
    assert "A" in result.updated


def test_merge_conflict_strategy_error_raises():
    with pytest.raises(MergeConflictError, match="CONFLICT"):
        merge_dicts({"A": "base"}, {"A": "other"}, strategy=ConflictStrategy.ERROR)


# ---------------------------------------------------------------------------
# MergeConflict str
# ---------------------------------------------------------------------------

def test_conflict_str_contains_key_and_values():
    c = MergeConflict(key="SECRET", ours="old", theirs="new")
    s = str(c)
    assert "SECRET" in s
    assert "old" in s
    assert "new" in s


# ---------------------------------------------------------------------------
# merge_dicts — empty inputs
# ---------------------------------------------------------------------------

def test_merge_empty_other_unchanged():
    base = {"X": "1", "Y": "2"}
    result = merge_dicts(base, {})
    assert result.merged == base
    assert result.added == []
    assert result.conflicts == []


def test_merge_empty_base_all_added():
    result = merge_dicts({}, {"A": "1", "B": "2"})
    assert set(result.added) == {"A", "B"}
    assert result.merged == {"A": "1", "B": "2"}
