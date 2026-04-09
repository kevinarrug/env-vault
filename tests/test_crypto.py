"""Unit tests for env_vault.crypto module."""

import pytest
from env_vault.crypto import encrypt, decrypt


PASSPHRASE = "super-secret-passphrase"
PLAINTEXT = "my_database_password_123!"


def test_encrypt_returns_string():
    token = encrypt(PLAINTEXT, PASSPHRASE)
    assert isinstance(token, str)
    assert len(token) > 0


def test_encrypt_produces_unique_tokens():
    token1 = encrypt(PLAINTEXT, PASSPHRASE)
    token2 = encrypt(PLAINTEXT, PASSPHRASE)
    assert token1 != token2, "Each encryption call should produce a unique token."


def test_decrypt_roundtrip():
    token = encrypt(PLAINTEXT, PASSPHRASE)
    result = decrypt(token, PASSPHRASE)
    assert result == PLAINTEXT


def test_decrypt_wrong_passphrase_raises():
    token = encrypt(PLAINTEXT, PASSPHRASE)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong-passphrase")


def test_decrypt_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid token"):
        decrypt("not-valid-base64!!!", PASSPHRASE)


def test_decrypt_truncated_token_raises():
    import base64
    short_token = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="Invalid token"):
        decrypt(short_token, PASSPHRASE)


def test_encrypt_empty_string():
    token = encrypt("", PASSPHRASE)
    assert decrypt(token, PASSPHRASE) == ""


def test_encrypt_unicode():
    unicode_text = "пароль_🔑_secret"
    token = encrypt(unicode_text, PASSPHRASE)
    assert decrypt(token, PASSPHRASE) == unicode_text
