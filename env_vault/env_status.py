"""Key status aggregation — combines lock, freeze, expiry, deprecation and TTL info."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from env_vault.env_lock import is_locked
from env_vault.env_freeze import is_frozen
from env_vault.expiry import is_expired, get_expiry
from env_vault.env_deprecate import is_deprecated, get_deprecation
from env_vault.ttl import get_ttl


@dataclass
class KeyStatus:
    key: str
    locked: bool = False
    frozen: bool = False
    expired: bool = False
    deprecated: bool = False
    ttl_remaining: Optional[float] = None
    deprecation_message: Optional[str] = None
    expiry_timestamp: Optional[float] = None
    extra: dict = field(default_factory=dict)

    @property
    def active(self) -> bool:
        """Return True when the key is usable (not expired, not deprecated)."""
        return not self.expired and not self.deprecated

    def summary(self) -> str:
        parts = []
        if self.locked:
            parts.append("locked")
        if self.frozen:
            parts.append("frozen")
        if self.expired:
            parts.append("expired")
        if self.deprecated:
            msg = f"deprecated({self.deprecation_message})" if self.deprecation_message else "deprecated"
            parts.append(msg)
        if self.ttl_remaining is not None:
            parts.append(f"ttl={self.ttl_remaining:.0f}s")
        return ", ".join(parts) if parts else "ok"

    def __str__(self) -> str:
        return f"<KeyStatus key={self.key!r} {self.summary()}>"


def get_status(vault_dir: str, key: str) -> KeyStatus:
    """Collect all status flags for *key* in the given vault directory."""
    vd = Path(vault_dir)

    locked = is_locked(str(vd), key)
    frozen = is_frozen(str(vd), key)

    expiry_info = get_expiry(str(vd), key)
    expired = expiry_info is not None and expiry_info.expired
    expiry_ts = expiry_info.expires_at if expiry_info else None

    deprecated = is_deprecated(str(vd), key)
    dep_info = get_deprecation(str(vd), key)
    dep_msg = dep_info.message if dep_info else None

    ttl = get_ttl(str(vd), key)  # returns remaining seconds or None

    return KeyStatus(
        key=key,
        locked=locked,
        frozen=frozen,
        expired=expired,
        deprecated=deprecated,
        ttl_remaining=ttl,
        deprecation_message=dep_msg,
        expiry_timestamp=expiry_ts,
    )


def get_all_statuses(vault_dir: str, keys: list[str]) -> list[KeyStatus]:
    """Return a status record for every key in *keys*."""
    return [get_status(vault_dir, k) for k in keys]
