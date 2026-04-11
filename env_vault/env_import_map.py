"""Key remapping/aliasing during import operations."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class MapResult:
    applied: Dict[str, str] = field(default_factory=dict)   # old_key -> new_key
    skipped: List[str] = field(default_factory=list)         # keys with no mapping
    warnings: List[str] = field(default_factory=list)

    @property
    def has_remaps(self) -> bool:
        return bool(self.applied)

    def summary(self) -> str:
        parts = []
        if self.applied:
            parts.append(f"{len(self.applied)} key(s) remapped")
        if self.skipped:
            parts.append(f"{len(self.skipped)} key(s) passed through unchanged")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        return ", ".join(parts) if parts else "no changes"


def _map_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".import_map.json"


def _load_map(vault_dir: str) -> Dict[str, str]:
    p = _map_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_map(vault_dir: str, mapping: Dict[str, str]) -> None:
    _map_path(vault_dir).write_text(json.dumps(mapping, indent=2, sort_keys=True))


def set_mapping(vault_dir: str, source_key: str, target_key: str) -> bool:
    """Add or update a mapping from source_key -> target_key. Returns True if new."""
    mapping = _load_map(vault_dir)
    is_new = source_key not in mapping
    mapping[source_key] = target_key
    _save_map(vault_dir, mapping)
    return is_new


def remove_mapping(vault_dir: str, source_key: str) -> bool:
    """Remove a mapping. Returns True if it existed."""
    mapping = _load_map(vault_dir)
    if source_key not in mapping:
        return False
    del mapping[source_key]
    _save_map(vault_dir, mapping)
    return True


def get_mappings(vault_dir: str) -> Dict[str, str]:
    return _load_map(vault_dir)


def apply_map(
    vault_dir: str,
    data: Dict[str, str],
    strict: bool = False,
) -> Tuple[Dict[str, str], MapResult]:
    """Apply stored mappings to *data*, returning remapped dict and a MapResult."""
    mapping = _load_map(vault_dir)
    result: Dict[str, str] = {}
    report = MapResult()

    for key, value in data.items():
        if key in mapping:
            new_key = mapping[key]
            if new_key in result:
                report.warnings.append(
                    f"Collision: '{key}' -> '{new_key}' already set; skipping"
                )
                continue
            result[new_key] = value
            report.applied[key] = new_key
        else:
            if strict:
                report.warnings.append(f"'{key}' has no mapping and strict=True; skipping")
            else:
                result[key] = value
                report.skipped.append(key)

    return result, report
