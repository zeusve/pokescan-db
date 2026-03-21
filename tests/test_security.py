from src.security import hash_password, verify_password


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
