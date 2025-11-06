import sys, os
import pytest

# ensure the app package can be imported when running from subdirectories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utilities.security import hashPassword, verifyPassword


# this test checks that hashPassword returns a non-empty string different from the original password
def test_hash_password_generates_hash():
    plain_pw = "supersecret123"
    hashed_pw = hashPassword(plain_pw)

    assert isinstance(hashed_pw, str)
    assert hashed_pw != plain_pw
    assert hashed_pw.startswith("$2b$") or hashed_pw.startswith("$2a$")  # bcrypt hash prefix


# this test checks that verifyPassword correctly validates a matching password
def test_verify_password_correct_match():
    plain_pw = "mypassword"
    hashed_pw = hashPassword(plain_pw)

    assert verifyPassword(plain_pw, hashed_pw) is True


# this test checks that verifyPassword fails for an incorrect password
def test_verify_password_incorrect_match():
    plain_pw = "mypassword"
    hashed_pw = hashPassword(plain_pw)

    assert verifyPassword("wrongpassword", hashed_pw) is False


# this test checks that hashing the same password twice produces different hashes (salted)
def test_hashing_same_password_twice_is_different():
    pw = "repeatpass"
    hash1 = hashPassword(pw)
    hash2 = hashPassword(pw)

    assert hash1 != hash2  # bcrypt uses random salts
    assert verifyPassword(pw, hash1)
    assert verifyPassword(pw, hash2)
