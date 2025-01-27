import os
import logging
from cryptography.fernet import Fernet
import time

# Generate and store an encryption key
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Load the encryption key
def load_key():
    return open("key.key", "rb").read()

# Encrypt data
def encrypt_data(data):
    key = load_key()
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

# Decrypt data
def decrypt_data(encrypted_data):
    key = load_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode()

# Log access attempts
def log_access(user, action, status="Success"):
    logging.basicConfig(filename="access_log.txt", level=logging.INFO, 
                        format="%(asctime)s - %(user)s - %(action)s - %(status)s")
    logging.info("", extra={"user": user, "action": action, "status": status})

# Mock function to simulate data access
def access_data(user, action, data):
    try:
        log_access(user, action)
        encrypted = encrypt_data(data)
        decrypted = decrypt_data(encrypted)
        return decrypted
    except Exception as e:
        log_access(user, action, status="Failed")
        raise e

# Example usage
if __name__ == "__main__":
    generate_key()  # Generate a key (run once)

    # Simulate access
    try:
        user_data = access_data("user1", "Read", "Sensitive Information")
        print("Decrypted Data:", user_data)
    except Exception as error:
        print("Access Denied:", error)
