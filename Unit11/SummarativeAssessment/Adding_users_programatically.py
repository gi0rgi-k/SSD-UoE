def add_user(username, plain_password, company_id):
    """Add a user to the repository with a hashed password."""
    DATA_REPOSITORY["users"][username] = {
        "password": hashlib.sha256(plain_password.encode()).hexdigest(),
        "company_id": company_id
    }

# Example usage:
add_user("new_user", "mypassword", "1234")
