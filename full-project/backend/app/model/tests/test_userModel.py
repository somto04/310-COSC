# Integration and Unit Tests for User Model
# This file contains a unit test which tests all getters and setters in the user model

import pytest
from ..user import user

def test_userGetterSetter():
    newUser = user(1, "Somto", 21, "somto@gmail.com", "userSomto", "encryptedpassword")
    assert newUser.userId == 1
    assert newUser.name == "Somto"
    assert newUser.age == 21
    assert newUser.email == "somto@gmail.com"
    assert newUser.username == "userSomto"
    assert newUser.password == "encryptedpassword"
    assert newUser.penaltiesCount == 0
