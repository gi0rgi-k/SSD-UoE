
import requests

# Fires Brute Force Attack on the system to see if login will work after the attack 
# or if system has protections (such as rate limiting) implemented to defend against it

def test_brute_force_attack():
    url = "http://127.0.0.1:5000/verify_company_id"
    username = "customer1"
    predefined_passwords = ["password123", "admin123", "CustomerTest"]

    for password in predefined_passwords:
        response = requests.post(url, json={"username": username, "company_id": "91011"})
        if response.status_code == 200:
            print(f"Brute force successful with password: {password}")
            break
        else:
            print(f"Failed attempt with password: {password}")

"""
Sends a crafted payload ({"username": "' OR '1'='1", "company_id": "91011"}) designed to bypass authentication by exploiting 
improperly sanitized input in SQL queries. Checks if the server returns a 200 response and 
indicates success in the response body ("success" in response.json()["status"]).
This simulation tests if the input fields are properly sanitized to prevent malicious SQL queries. 
However, it's only a simulation since SQL database is not used in the App.
"""


def test_sql_injection():
    url = "http://127.0.0.1:5000/verify_company_id"
    payload = {"username": "' OR '1'='1", "company_id": "91011"}
    response = requests.post(url, json=payload)

    if response.status_code == 200 and "success" in response.json()["status"]:
        print("SQL Injection successful!")
    else:
        print("SQL Injection mitigated.")

"""
Sends 1000 rapid requests to the /verify_company_id endpoint. 
Logs the status of each response to monitor how the server handles the load. 
Tests if rate limiting or other mechanisms are in place to mitigate DoS attacks.
"""


def test_dos_attack():
    url = "http://127.0.0.1:5000/verify_company_id"
    for _ in range(1000):  # High number of requests
        response = requests.post(url, json={"username": "customer1", "company_id": "91011"})
        print(f"Request status: {response.status_code}")

"""
Sends a payload ({"username": "<script>alert('XSS')</script>", "company_id": "91011"}) 
containing a JavaScript <script> tag to the server.
Tests if the server reflects unescaped user input in its responses, making it vulnerable to XSS attacks.
"""

def test_payload_injection():
    url = "http://127.0.0.1:5000/verify_company_id"
    payload = {"username": "<script>alert('XSS')</script>", "company_id": "91011"}
    response = requests.post(url, json=payload)

    if "<script>" in response.text:
        print("XSS vulnerability detected!")
    else:
        print("Payload injection mitigated.")

# Run the tests
if __name__ == "__main__":
    test_brute_force_attack()
    test_sql_injection()
    test_dos_attack()
    test_payload_injection()
