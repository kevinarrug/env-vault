"""Encryption and decryption utilities for env-vault using AES-256-GCM."""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
ITERATIONS = 600_000


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a passphrase using PBKDF2-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(passphrase.encode())


def encrypt(plaintext: str, passphrase: str) -> str:
    """Encrypt plaintext and return a base64-encoded token (salt + nonce + ciphertext)."""
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    token = base64.b64encode(salt + nonce + ciphertext).decode()
    return token


def decrypt(token: str, passphrase: str) -> str:
    """Decrypt a base64-encoded token and return the original plaintext."""
    try:
        raw = base64.b64decode(token.encode())
    except Exception as exc:
        raise ValueError("Invalid token: base64 decoding failed.") from exc

    if len(raw) < SALT_SIZE + NONCE_SIZE + 16:
        raise ValueError("Invalid token: data too short.")

    salt = raw[:SALT_SIZE]
    nonce = raw[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = raw[SALT_SIZE + NONCE_SIZE:]
    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise ValueError("Decryption failed: wrong passphrase or corrupted data.") from exc
    return plaintext.decode()
