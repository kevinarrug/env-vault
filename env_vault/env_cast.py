"""Type casting for environment variable values stored in the vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_SUPPORTED_TYPES = ("str", "int", "float", "bool", "list")


@dataclass
class CastResult:
    key: str
    raw: str
    cast_type: str
    value: Any
    success: bool
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return f"{self.key} ({self.cast_type}): {self.value!r}"
        return f"{self.key} cast error: {self.error}"


def cast_value(raw: str, cast_type: str) -> Any:
    """Cast a raw string value to the given type."""
    if cast_type == "str":
        return raw
    if cast_type == "int":
        return int(raw)
    if cast_type == "float":
        return float(raw)
    if cast_type == "bool":
        if raw.lower() in ("1", "true", "yes", "on"):
            return True
        if raw.lower() in ("0", "false", "no", "off"):
            return False
        raise ValueError(f"Cannot cast {raw!r} to bool")
    if cast_type == "list":
        return [item.strip() for item in raw.split(",") if item.strip()]
    raise ValueError(f"Unsupported cast type: {cast_type!r}")


def cast_key(vault, key: str, cast_type: str, passphrase: str) -> CastResult:
    """Retrieve and cast a single key from the vault."""
    raw = vault.get(key, passphrase)
    try:
        value = cast_value(raw, cast_type)
        return CastResult(key=key, raw=raw, cast_type=cast_type, value=value, success=True)
    except (ValueError, TypeError) as exc:
        return CastResult(
            key=key, raw=raw, cast_type=cast_type, value=None, success=False, error=str(exc)
        )


def cast_all(vault, schema: Dict[str, str], passphrase: str) -> List[CastResult]:
    """Cast multiple keys according to a type schema dict {key: type}."""
    results: List[CastResult] = []
    for key, cast_type in schema.items():
        results.append(cast_key(vault, key, cast_type, passphrase))
    return results


def cast_to_dict(vault, schema: Dict[str, str], passphrase: str) -> Dict[str, Any]:
    """Return a plain dict of cast values; raises on first failure."""
    out: Dict[str, Any] = {}
    for result in cast_all(vault, schema, passphrase):
        if not result.success:
            raise ValueError(str(result))
        out[result.key] = result.value
    return out
