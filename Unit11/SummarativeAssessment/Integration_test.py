import pytest
from flask import Flask
from main9 import app, DATA_REPOSITORY, SECURITY_ENABLED

"""
Hardcode the toggle to 'True' for the test. So that the security features (e.g., rate limiting, brute-force protection) 
are enabled for every test case.
"""

@pytest.fixture(autouse=True)
def enable_security():
    """Ensure SECURITY_ENABLED is set to True for all tests."""
    global SECURITY_ENABLED
    SECURITY_ENABLED = True

# Allows testing of the Flask application endpoints in isolation from a real network environment.

@pytest.fixture
def client():
    """Set up the test client for Flask app."""
    with app.test_client() as client:
        yield client


# Confirm that valid users can verify their company_id successfully.
def test_verify_company_id_success(client):
    data = {"username": "customer1", "company_id": "91011"}
    response = client.post('/verify_company_id', json=data)
    assert response.status_code == 200
    assert response.json["status"] == "success"

# Verify that the system does not authenticate users with invalid or incorrect data.

def test_verify_company_id_failure(client):
    data = {"username": "customer1", "company_id": "wrong_id"}
    response = client.post('/verify_company_id', json=data)
    assert response.status_code == 400
    assert response.json["status"] == "fail"


# Check rate limiting
@pytest.mark.parametrize("request_count", [15])
def test_rate_limiting(client, request_count):
    for i in range(request_count):
        response = client.post(
            '/verify_company_id',
            json={"username": "customer1", "company_id": "91011"},
            headers={"REMOTE_ADDR": "127.0.0.1"}  # Simulate same IP address
        )
        if i >= 10:  # Assuming rate limit is 10 requests per window
            assert response.status_code == 429
            break
