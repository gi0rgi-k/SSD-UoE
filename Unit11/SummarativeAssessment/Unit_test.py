import pytest
from unittest.mock import patch
import hashlib
import json
from main9 import Authentication, BruteForceProtection, hash_password, DATA_REPOSITORY


# Test if hashing function works correcly
def test_hash_password():
    password = "test123"
    expected_hash = hashlib.sha256(password.encode()).hexdigest()
    assert hash_password(password) == expected_hash


# Test if login functionality works correctly in the main code
def test_login_success():
    username = "customer1"
    password = "CustomerTest"
    assert Authentication.login(username, password) is True


def test_login_fail_wrong_password():
    username = "customer1"
    password = "WrongPassword"
    assert Authentication.login(username, password) is False


def test_login_fail_user_locked_out():
    username = "customer1"
    password = "CustomerTest"
    BruteForceProtection.MAX_ATTEMPTS = 2

    # Simulate failed login attempts
    Authentication.login(username, "WrongPassword")
    Authentication.login(username, "WrongPassword")

    # User should now be locked out if successful
    assert Authentication.login(username, password) is False


# Unit test brute force protection
def test_brute_force_protection():
    username = "customer1"
    BruteForceProtection.MAX_ATTEMPTS = 2

    for _ in range(3):
        BruteForceProtection.record_failed_attempt(username)

    assert not BruteForceProtection.can_attempt(username)


def test_reset_attempts():
    username = "customer1"
    BruteForceProtection.reset_attempts(username)
    assert BruteForceProtection.can_attempt(username)
