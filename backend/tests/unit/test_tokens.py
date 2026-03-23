import uuid
import pytest
import jwt as pyjwt
from app.utils.tokens import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token, generate_verification_token


def test_access_roundtrip():
    uid = uuid.uuid4()
    token = create_access_token(uid, "buyer")
    payload = decode_access_token(token)
    assert payload["sub"] == str(uid) and payload["role"] == "buyer"

def test_refresh_roundtrip():
    uid = uuid.uuid4()
    payload = decode_refresh_token(create_refresh_token(uid))
    assert payload["sub"] == str(uid)

def test_refresh_as_access_fails():
    with pytest.raises(pyjwt.InvalidTokenError):
        decode_access_token(create_refresh_token(uuid.uuid4()))

def test_access_as_refresh_fails():
    with pytest.raises(pyjwt.InvalidTokenError):
        decode_refresh_token(create_access_token(uuid.uuid4(), "buyer"))

def test_invalid_token():
    with pytest.raises(pyjwt.PyJWTError):
        decode_access_token("invalid")

def test_verification_token_length():
    assert len(generate_verification_token()) > 30

def test_tokens_unique():
    t1 = create_access_token(uuid.uuid4(), "buyer")
    t2 = create_access_token(uuid.uuid4(), "buyer")
    assert t1 != t2

def test_seller_role():
    uid = uuid.uuid4()
    payload = decode_access_token(create_access_token(uid, "seller"))
    assert payload["role"] == "seller"
