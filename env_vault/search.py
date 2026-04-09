"""Search and filter environment variables stored in a vault."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_vault.vault import Vault


@dataclass
class SearchResult:
    key: str
    value: str
    matched_by: str  # 'key' | 'value' | 'both'


def search_by_key(
    vault: Vault,
    passphrase: str,
    pattern: str,
    *,
    glob: bool = False,
) -> List[SearchResult]:
    """Return entries whose key matches *pattern*.

    When *glob* is True the pattern is treated as a shell-style glob
    (e.g. ``AWS_*``), otherwise it is compiled as a regular expression.
    """
    results: List[SearchResult] = []
    keys = vault.list_keys()
    for key in keys:
        if glob:
            matched = fnmatch.fnmatch(key, pattern)
        else:
            matched = bool(re.search(pattern, key))
        if matched:
            value = vault.get(key, passphrase)
            results.append(SearchResult(key=key, value=value, matched_by="key"))
    return results


def search_by_value(
    vault: Vault,
    passphrase: str,
    pattern: str,
    *,
    glob: bool = False,
) -> List[SearchResult]:
    """Return entries whose decrypted value matches *pattern*."""
    results: List[SearchResult] = []
    keys = vault.list_keys()
    for key in keys:
        value = vault.get(key, passphrase)
        if glob:
            matched = fnmatch.fnmatch(value, pattern)
        else:
            matched = bool(re.search(pattern, value))
        if matched:
            results.append(SearchResult(key=key, value=value, matched_by="value"))
    return results


def search(
    vault: Vault,
    passphrase: str,
    pattern: str,
    *,
    glob: bool = False,
) -> List[SearchResult]:
    """Search both keys and values; deduplicate with *matched_by='both'*."""
    by_key: Dict[str, SearchResult] = {
        r.key: r for r in search_by_key(vault, passphrase, pattern, glob=glob)
    }
    by_val: Dict[str, SearchResult] = {
        r.key: r for r in search_by_value(vault, passphrase, pattern, glob=glob)
    }
    merged: Dict[str, SearchResult] = {}
    all_keys = set(by_key) | set(by_val)
    for key in sorted(all_keys):
        if key in by_key and key in by_val:
            merged[key] = SearchResult(
                key=key, value=by_key[key].value, matched_by="both"
            )
        elif key in by_key:
            merged[key] = by_key[key]
        else:
            merged[key] = by_val[key]
    return list(merged.values())
