"""Secure sharing of individual vault entries via time-limited tokens."""

import base64
import json
import time
from pathlib import Path
from typing import Optional

from env_vault.crypto import derive_key, encrypt, decrypt

_SHARE_VERSION = 1
DEFAULT_TTL = 3600  # seconds


def create_share_token(
    key: str,
    value: str,
    passphrase: str,
    ttl: int = DEFAULT_TTL,
) -> str:
    """Encrypt a key/value pair into a shareable, time-limited token."""
    payload = json.dumps({
        "v": _SHARE_VERSION,
        "key": key,
        "value": value,
        "exp": int(time.time()) + ttl,
    })
    token_bytes = encrypt(payload, passphrase)
    return base64.urlsafe_b64encode(token_bytes).decode()


def decode_share_token(
    token: str,
    passphrase: str,
) -> dict:
    """Decode and validate a share token.  Returns {key, value}.

    Raises:
        ValueError: if the token is expired or the passphrase is wrong.
        Exception: propagated from decrypt() on integrity failure.
    """
    raw = base64.urlsafe_b64decode(token.encode())
    plaintext = decrypt(raw, passphrase)  # raises on bad passphrase
    payload = json.loads(plaintext)

    if int(time.time()) > payload["exp"]:
        raise ValueError("Share token has expired.")

    return {"key": payload["key"], "value": payload["value"]}


def save_share_token(token: str, path: Path) -> None:
    """Persist a share token to a file."""
    path.write_text(token)


def load_share_token(path: Path) -> str:
    """Load a share token from a file."""
    if not path.exists():
        raise FileNotFoundError(f"Token file not found: {path}")
    return path.read_text().strip()
