"""Resolve environment variable references within vault values.

Supports ${KEY} syntax for referencing other vault keys.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


@dataclass
class ResolveResult:
    key: str
    raw: str
    resolved: str
    references: List[str] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return self.resolved

    @property
    def has_unresolved(self) -> bool:
        return len(self.unresolved) > 0


def resolve_value(
    key: str,
    raw: str,
    secrets: Dict[str, str],
    *,
    max_depth: int = 10,
) -> ResolveResult:
    """Resolve ${REF} placeholders in *raw* using *secrets* dict."""
    references: List[str] = []
    unresolved: List[str] = []
    visited: List[str] = [key]

    def _expand(value: str, depth: int) -> str:
        if depth > max_depth:
            return value
        def _sub(m: re.Match) -> str:
            ref = m.group(1)
            if ref in visited:
                unresolved.append(ref)
                return m.group(0)
            if ref not in secrets:
                if ref not in unresolved:
                    unresolved.append(ref)
                return m.group(0)
            if ref not in references:
                references.append(ref)
            visited.append(ref)
            result = _expand(secrets[ref], depth + 1)
            visited.pop()
            return result
        return _REF_PATTERN.sub(_sub, value)

    resolved = _expand(raw, 0)
    return ResolveResult(
        key=key,
        raw=raw,
        resolved=resolved,
        references=references,
        unresolved=unresolved,
    )


def resolve_all(
    secrets: Dict[str, str],
    *,
    max_depth: int = 10,
) -> Dict[str, ResolveResult]:
    """Resolve all values in *secrets*, returning a mapping of results."""
    return {
        k: resolve_value(k, v, secrets, max_depth=max_depth)
        for k, v in secrets.items()
    }
