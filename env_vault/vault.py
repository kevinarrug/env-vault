"""Vault model: load, save, and manage versioned encrypted env entries."""

import json
import time
from pathlib import Path
from typing import Any

from env_vault.crypto import encrypt, decrypt

DEFAULT_VAULT_FILE = ".env-vault.json"


class Vault:
    """Manages an encrypted, versioned store of environment variables."""

    def __init__(self, path: str = DEFAULT_VAULT_FILE) -> None:
        self.path = Path(path)
        self._data: dict[str, Any] = {"version": 1, "entries": {}}

    def load(self) -> None:
        """Load vault data from disk."""
        if self.path.exists():
            with self.path.open("r") as fh:
                self._data = json.load(fh)

    def save(self) -> None:
        """Persist vault data to disk."""
        with self.path.open("w") as fh:
            json.dump(self._data, fh, indent=2)

    def set(self, key: str, value: str, passphrase: str) -> None:
        """Encrypt and store a variable, appending to its version history."""
        token = encrypt(value, passphrase)
        entry = self._data["entries"].setdefault(key, {"history": []})
        entry["history"].append({"token": token, "timestamp": time.time()})
        entry["current"] = token

    def get(self, key: str, passphrase: str) -> str:
        """Retrieve and decrypt the current value for a key."""
        entry = self._data["entries"].get(key)
        if entry is None:
            raise KeyError(f"Key '{key}' not found in vault.")
        return decrypt(entry["current"], passphrase)

    def history(self, key: str, passphrase: str) -> list[dict]:
        """Return decrypted version history for a key."""
        entry = self._data["entries"].get(key)
        if entry is None:
            raise KeyError(f"Key '{key}' not found in vault.")
        result = []
        for record in entry["history"]:
            result.append({
                "value": decrypt(record["token"], passphrase),
                "timestamp": record["timestamp"],
            })
        return result

    def delete(self, key: str) -> None:
        """Remove a key from the vault."""
        if key not in self._data["entries"]:
            raise KeyError(f"Key '{key}' not found in vault.")
        del self._data["entries"][key]

    def list_keys(self) -> list[str]:
        """Return all stored key names."""
        return list(self._data["entries"].keys())
