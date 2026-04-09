"""env-vault: encrypt and version environment variables across projects."""

from __future__ import annotations

__version__ = "0.2.0"
__all__ = ["Vault", "encrypt", "decrypt", "derive_key", "format_output", "import_dotenv", "import_json"]

from env_vault.crypto import decrypt, derive_key, encrypt
from env_vault.export import format_output, import_dotenv, import_json
from env_vault.vault import Vault
