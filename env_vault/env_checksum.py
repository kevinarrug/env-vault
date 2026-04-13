"""Checksum tracking for vault keys — detect external tampering."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


def _checksum_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".checksums.json"


def _load_checksums(vault_dir: str) -> dict:
    p = _checksum_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_checksums(vault_dir: str, data: dict) -> None:
    _checksum_path(vault_dir).write_text(json.dumps(data, indent=2))


def _compute(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def record_checksum(vault_dir: str, key: str, value: str) -> str:
    """Store checksum for key's value. Returns the hex digest."""
    data = _load_checksums(vault_dir)
    digest = _compute(value)
    data[key] = digest
    _save_checksums(vault_dir, data)
    return digest


def get_checksum(vault_dir: str, key: str) -> Optional[str]:
    """Return stored checksum for key, or None if not recorded."""
    return _load_checksums(vault_dir).get(key)


def remove_checksum(vault_dir: str, key: str) -> bool:
    """Remove stored checksum. Returns True if it existed."""
    data = _load_checksums(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_checksums(vault_dir, data)
    return True


@dataclass
class ChecksumVerification:
    key: str
    expected: Optional[str]
    actual: str
    tampered: bool

    def __str__(self) -> str:
        status = "TAMPERED" if self.tampered else "OK"
        return f"{self.key}: {status}"


def verify_checksum(vault_dir: str, key: str, current_value: str) -> ChecksumVerification:
    """Compare stored checksum against current value."""
    expected = get_checksum(vault_dir, key)
    actual = _compute(current_value)
    tampered = expected is not None and expected != actual
    return ChecksumVerification(key=key, expected=expected, actual=actual, tampered=tampered)


def verify_all(vault_dir: str, current_values: dict[str, str]) -> list[ChecksumVerification]:
    """Verify all keys that have stored checksums."""
    data = _load_checksums(vault_dir)
    results = []
    for key, expected in data.items():
        value = current_values.get(key, "")
        actual = _compute(value)
        results.append(ChecksumVerification(
            key=key, expected=expected, actual=actual,
            tampered=(expected != actual)
        ))
    return results
