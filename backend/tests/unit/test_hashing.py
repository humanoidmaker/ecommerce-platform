from app.utils.hashing import hash_password, verify_password

def test_hash_roundtrip():
    h = hash_password("secret123")
    assert verify_password("secret123", h)

def test_wrong_password():
    h = hash_password("correct")
    assert not verify_password("wrong", h)

def test_hashes_differ():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2

def test_hash_not_plaintext():
    h = hash_password("password")
    assert "password" not in h

def test_hash_length():
    assert len(hash_password("x")) > 20
