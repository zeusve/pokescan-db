from datetime import timedelta
from unittest.mock import patch

from src.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_not_plaintext():
    password = "my_secret_password"
    hashed = hash_password(password)
    assert hashed != password


def test_hash_is_bcrypt_format():
    hashed = hash_password("test")
    assert hashed.startswith("$2b$")


def test_hash_is_nondeterministic():
    password = "same_password"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2


def test_verify_correct_password():
    password = "correct_horse_battery_staple"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("real_password")
    assert verify_password("wrong_password", hashed) is False


def test_create_and_decode_token():
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user@example.com"
    assert "exp" in decoded


def test_token_contains_custom_claims():
    data = {"sub": "user42", "role": "admin"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded["sub"] == "user42"
    assert decoded["role"] == "admin"


def test_token_with_custom_expiry():
    data = {"sub": "user@example.com"}
    token = create_access_token(data, expires_delta=timedelta(hours=2))
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user@example.com"


def test_decode_expired_token():
    data = {"sub": "user@example.com"}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    decoded = decode_token(token)
    assert decoded is None


def test_decode_invalid_token():
    decoded = decode_token("not.a.valid.token")
    assert decoded is None


def test_decode_tampered_token():
    token = create_access_token({"sub": "user@example.com"})
    tampered = token[:-4] + "XXXX"
    decoded = decode_token(tampered)
    assert decoded is None


def test_create_token_does_not_mutate_input():
    data = {"sub": "user@example.com"}
    original = data.copy()
    create_access_token(data)
    assert data == original
