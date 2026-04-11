"""Dependency tracking between environment variable keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Set


def _deps_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_depends.json"


def _load_deps(vault_dir: str) -> Dict[str, List[str]]:
    p = _deps_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deps(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _deps_path(vault_dir).write_text(json.dumps(data, indent=2))


def add_dependency(vault_dir: str, key: str, depends_on: str) -> bool:
    """Record that *key* depends on *depends_on*. Returns True if newly added."""
    data = _load_deps(vault_dir)
    deps = data.setdefault(key, [])
    if depends_on in deps:
        return False
    deps.append(depends_on)
    _save_deps(vault_dir, data)
    return True


def remove_dependency(vault_dir: str, key: str, depends_on: str) -> bool:
    """Remove a dependency edge. Returns True if it existed."""
    data = _load_deps(vault_dir)
    deps = data.get(key, [])
    if depends_on not in deps:
        return False
    deps.remove(depends_on)
    if not deps:
        data.pop(key, None)
    _save_deps(vault_dir, data)
    return True


def get_dependencies(vault_dir: str, key: str) -> List[str]:
    """Return keys that *key* directly depends on."""
    return list(_load_deps(vault_dir).get(key, []))


def get_dependents(vault_dir: str, key: str) -> List[str]:
    """Return keys that directly depend on *key*."""
    data = _load_deps(vault_dir)
    return [k for k, deps in data.items() if key in deps]


def resolve_order(vault_dir: str, keys: Optional[List[str]] = None) -> List[str]:
    """Topological sort of *keys* respecting dependency order.

    Raises ValueError on cycles.
    """
    data = _load_deps(vault_dir)
    if keys is None:
        all_keys: Set[str] = set(data.keys())
        for deps in data.values():
            all_keys.update(deps)
        keys = list(all_keys)

    visited: Set[str] = set()
    stack: Set[str] = set()
    order: List[str] = []

    def visit(node: str) -> None:
        if node in stack:
            raise ValueError(f"Dependency cycle detected involving '{node}'")
        if node in visited:
            return
        stack.add(node)
        for dep in data.get(node, []):
            visit(dep)
        stack.discard(node)
        visited.add(node)
        order.append(node)

    for k in keys:
        visit(k)
    return order
