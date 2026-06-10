from uuid import uuid4

from app.core.security import (
    create_access_token,
    decode_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    is_api_key,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("secure-password")
    assert verify_password("secure-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_jwt_roundtrip() -> None:
    user_id = uuid4()
    token = create_access_token(user_id)
    assert decode_token(token) == user_id


def test_api_key_generation() -> None:
    full_key, prefix, key_hash = generate_api_key()
    assert full_key.startswith("apk_")
    assert is_api_key(full_key)
    assert not is_api_key("eyJhbGciOiJIUzI1NiJ9")
    assert prefix == full_key[:12]
    assert key_hash == hash_api_key(full_key)
