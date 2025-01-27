import hashlib
import json
import random
import string
from threading import Thread
import time
from flask import Flask, request, jsonify
import requests
import threading
from werkzeug.serving import make_server
import logging
import re  


# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


# Data repository (JSON file as a simulation of a database)
DATA_REPOSITORY = {
    "users": {
        "admin": {   # Username of a user with Admin role
            "password": "0161e13f3124ae3455747b1a9ed78aa231253ae5c543cd28b9a6605835148299",  # Hashed password for "AdminPass"
            "company_id": "1234",
            "first_name": "Admin",
            "last_name": "User",
            "role": "Admin",
            "cart": {}
        },
        "clerk1": {  # Username of a user with Clerk role
            "password": "db9664c4d12af908907b27329688882cabc5b321d5343059900f5a18b8a3a61c",  # Hashed password for "ClerkTest"
            "company_id": "5678",
            "first_name": "Clerk",
            "last_name": "One",
            "role": "Clerk",
            "cart": {}
        },
        "customer1": {  # Username of a Customer
            "password": "0cca9350cff04c9342cf5da79016d83fe1fa58c8a64bc5cdf6a8c0fa59131b23",  # Hashed password for "CustomerTest"
            "company_id": "91011",
            "first_name": "Customer",
            "last_name": "One",
            "role": "Customer",
            "cart": {}
        }
    },
    "items": [
        {"item_id": 1, "name": "Shampoo", "category": "Hair Care", "price": 10.0},
        {"item_id": 2, "name": "Conditioner", "category": "Hair Care", "price": 12.0},
    ],
    "company_ids": ["1234", "5678", "91011"],  # Pre-verified company IDs inputted by Admin. Later used for Customer verification
    "sessions": {},  # {"username": "session_token"}
    "carts": {}  # {"username": [{"item_id": 1, "name": "Shampoo", "price": 10.0}]}. Lists items that user added to cart, count and sum of price
}


# Security toggle (will be set to by user input in the UI class. This will turn on/off hacker attack protection features)
SECURITY_ENABLED = None


# Flask API functions and events

app = Flask(__name__)

# Event to signal Flask server to stop automatically when Exiting the App (Python Software Foundation, 2025). 
# Starting and ending Flask server together with CLI UI ensures a better user experience with the App.
stop_event = threading.Event()  

def run_flask():
    """Run Flask server and stop it using stop_event."""
    server = make_server("127.0.0.1", 5000, app) # IP address and port to run locally on the laptop
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()  # Start the server in a separate thread
    print("Flask server running on http://127.0.0.1:5000")

    # Blocks until stop_event is set
    stop_event.wait()  

    # Shutdown the server when the event is triggered
    server.shutdown()
    server_thread.join()
    print("Flask server stopped.")

# REST API for company ID verification using Flask API (Pallets, 2010).
@app.route('/verify_company_id', methods=['POST'])
def verify_company_id_api():
    ip = request.remote_addr
    if SECURITY_ENABLED and RateLimiter.is_rate_limited(ip): #Returns rate limtied message only if security_enabled toggle is ON
        return jsonify({"status": "fail", "message": "Rate limit exceeded"}), 429

    data = request.json
    username = sanitize_input(data.get("username", "")) # Santize inputs when security_enabled is ON to protect against attacks
    company_id = sanitize_input(data.get("company_id", ""))
    user = DATA_REPOSITORY["users"].get(username) 

    if user and user["company_id"] == company_id:
        return jsonify({"status": "success", "message": "Company ID verified"}), 200 #Retrieve company_id from Repo and verify if it matches with input
    return jsonify({"status": "fail", "message": "Invalid Company ID"}), 400


# Function to save repository to a file (to simulate persistent storage)
def save_repository():
    """Save the current state of the data repository to a JSON file."""
    with open("data_repository.json", "w") as f:
        json.dump(DATA_REPOSITORY, f, indent=4)



# Hashing function
def hash_password(password: str) -> str:
    """Hash the password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# Generate random token (which will be used to identify user's unique session - which will be stored in the repo)
def generate_session_token() -> str:
    """Generate a random session token."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))



# User class
class User:
    def __init__(self, username: str, password: str, company_id: str):
        self.username = username
        self.password_hash = hash_password(password)
        self.company_id = company_id

    def save_to_repository(self): 
        """Save user to the data repository."""
        DATA_REPOSITORY["users"][self.username] = {
            "password": self.password_hash,
            "company_id": self.company_id
        }
        print(f"User {self.username} created successfully!")



# Login and Logout functionality
class Authentication:
    @staticmethod
    def login(username: str, password: str) -> bool:
        # Sanitize inputs to prevent injection attacks
        username = sanitize_input(username)
        password = sanitize_input(password)

        # Check lockout status in Secure Mode against Brute Force attacks
        if SECURITY_ENABLED and not BruteForceProtection.can_attempt(username):
            print(f"Login blocked: User {username} is locked out.")
            return False

        # Authenticate user
        user = DATA_REPOSITORY["users"].get(username)
        if user and user["password"] == hash_password(password):
            logging.info(f"User {username} logged in successfully.")  # Log successful login (function was defined above)
            if SECURITY_ENABLED:
                BruteForceProtection.reset_attempts(username) 
            token = generate_session_token() 
            DATA_REPOSITORY["sessions"][username] = token #store the generated session token in the repo if login is successful
            print(f"User {username} logged in successfully!")
            return True
        else:
            logging.warning(f"Failed login attempt for user {username}.")  # Log failed login


        # Log failed attempts in Secure Mode
        print("Invalid username or password.")
        if SECURITY_ENABLED:
            BruteForceProtection.record_failed_attempt(username) #count failed attempts for user lockout if secure mode is enabled
        return False


    @staticmethod
    def logout(username: str):
        """Log out the user and clear the session."""
        if username in DATA_REPOSITORY["sessions"]:
            del DATA_REPOSITORY["sessions"][username] # Deletes session token in the repo after the log out
            print(f"User {username} logged out successfully!")


# Multi-factor authentication
class MultiFactorAuthentication:
    @staticmethod
    def send_otp() -> str:
        """Simulate sending an OTP to the user."""
        otp = ''.join(random.choices(string.digits, k=6))
        print(f"OTP sent: {otp}")  # In a real system, this would be sent to the user via a different app
        return otp

    @staticmethod
    def verify_otp(input_otp: str, correct_otp: str) -> bool:
        """Compare the OTP entered by the user and generated by the app."""
        return input_otp == correct_otp


# Session management
class SessionManager:
    @staticmethod
    def start_session(username: str):
        """Start a session for a user and store the user's session token."""
        token = generate_session_token()
        DATA_REPOSITORY["sessions"][username] = token
        print(f"Session started for {username}. Token: {token}")

    @staticmethod
    def end_session(username: str):
        """End a session for a user and delete it from the repo."""
        if username in DATA_REPOSITORY["sessions"]:
            del DATA_REPOSITORY["sessions"][username]
            print(f"Session ended for {username}.")

class Hacker:
    @staticmethod
    def brute_force_attack(username: str):
        print(f"Starting brute force attack on user: {username}")

        # Check initial lockout status
        if SECURITY_ENABLED and not BruteForceProtection.can_attempt(username):
            print(f"Brute force attack blocked: User {username} is currently locked out.")
            return

        # Simulated brute force with predefined password attempts.
        # For simplicity, instead of a random combination of all characters, predefined list is used.
        # When hashed version of one of the pre-defined passwords matches user's actual hashed password in the Repo, the Attack succeeds.
        predefined_passwords = ["password123", "admin123", "CustomerTest"]
        for attempt in predefined_passwords:
            # Recheck lockout status before each attempt
            if SECURITY_ENABLED and not BruteForceProtection.can_attempt(username):
                print(f"Brute force attack blocked: User {username} is now locked out.")
                return

            print(f"Trying password: {attempt}")

            # Use Authentication.login to enforce security checks
            if Authentication.login(username, attempt):
                print(f"Brute force successful for user: {username} with password: {attempt}")
                return

            # Introduce a delay to allow lockout mechanisms to trigger. The delay also simulates a real-life scenario.
            time.sleep(2)  

        print(f"Brute force failed for user: {username}")


    @staticmethod
    def denial_of_service():
        print("Simulating Denial of Service (DoS) attack...")

        for i in range(15):
            response = requests.post(
                "http://127.0.0.1:5000/verify_company_id",
                json={"username": "customer1", "company_id": "91011"}
            )
            if not SECURITY_ENABLED:
                print(f"Request {i + 1}: Fake request sent to overload the system. Status: {response.status_code}")
            elif response.status_code == 429:
                print(f"Request {i + 1}: DoS attack mitigated. Rate limit reached.")
                break
            else:
                print(f"Request {i + 1}: Request processed successfully.")

    @staticmethod
    def api_injection_attack():
        fake_payload = {"username": "' OR '1'='1", "password": "' OR '1'='1"}
        print(f"Simulating API injection attack with payload: {fake_payload}")

        if not SECURITY_ENABLED:
            # Send a request to the vulnerable API endpoint
            response = requests.post("http://127.0.0.1:5000/verify_company_id", json=fake_payload)
            if response.status_code == 200 and "success" in response.json().get("status", ""):
                print(f"API injection successful with payload: {fake_payload}")
            else:
                print("API injection attempt failed.")
        else:
            print("API injection attack mitigated.")


    """
    The fake payload, such as ""username": "' OR '1'='1"" meaningfully reflects API Injection only in the context of a SQL-based database 
    that interprets queries, so above is just a simulation of how it would work in an actual eShop where data storage is based on SQL-based database.
    This wouldn't have the same affect in DATA_REPOSITORY because dictionary does not interpret strings as executable code; 
    it simply retrieves a value based on the provided key. As a result, even in "Insecure" mode, status response is 400 and not 200.

    The expectation is to return "API injection attack mitigated" in Secure mode since there is protection enabled. But even in Insecure mode
    it should return 400 response and "API injection attempt failed." due to Company ID not being specified in request, and this being a Json repository with dictionaries
    and not a SQL database.
    """


class BruteForceProtection:
    MAX_ATTEMPTS = 2  # Maximum allowed failed attempts
    LOCKOUT_TIME = 60  # Lockout time in seconds

    login_attempts = {}  # {"username": {"attempts": 0, "lockout_end": None}}

    @staticmethod
    def can_attempt(username: str) -> bool:
        user_attempts = BruteForceProtection.login_attempts.get(username, {"attempts": 0, "lockout_end": None})
        lockout_end = user_attempts.get("lockout_end")

        # Enforce lockout if the current time is before lockout_end
        if lockout_end and time.time() < lockout_end:
            print(f"User {username} is locked out until {time.ctime(lockout_end)}.")
            return False

        return True


    @staticmethod
    def record_failed_attempt(username: str): #count login attempts and show Lockout message if exceeds the maximum lockout number
        if username not in BruteForceProtection.login_attempts:
            BruteForceProtection.login_attempts[username] = {"attempts": 0, "lockout_end": None}

        user_attempts = BruteForceProtection.login_attempts[username]
        user_attempts["attempts"] += 1

        if user_attempts["attempts"] >= BruteForceProtection.MAX_ATTEMPTS:
            user_attempts["lockout_end"] = time.time() + BruteForceProtection.LOCKOUT_TIME
            print(f"User {username} is locked out for {BruteForceProtection.LOCKOUT_TIME} seconds.")

    @staticmethod
    def reset_attempts(username: str): #delete/reset the login count
        if username in BruteForceProtection.login_attempts:
            del BruteForceProtection.login_attempts[username]


class RateLimiter:
    REQUEST_LIMIT = 10  # Max requests per user
    TIME_WINDOW = 30    # Time window in seconds

    request_log = {}  # {"IP": {"count": 0, "first_request_time": None}}

    @staticmethod
    def is_rate_limited(ip: str) -> bool:
        now = time.time()
        user_log = RateLimiter.request_log.get(ip, {"count": 0, "first_request_time": now})
        time_since_first = now - user_log["first_request_time"]

        if time_since_first > RateLimiter.TIME_WINDOW:
            RateLimiter.request_log[ip] = {"count": 1, "first_request_time": now}
            return False

        if user_log["count"] >= RateLimiter.REQUEST_LIMIT:
            print(f"IP {ip} is rate-limited. Try again later.")
            return True

        user_log["count"] += 1
        RateLimiter.request_log[ip] = user_log
        return False

def sanitize_input(data: str) -> str:
    return ''.join(c for c in data if c.isalnum() or c.isspace())


class CartOperations:
    @staticmethod
    def add_to_cart(username: str, item_id: int):
        """Add an item to the user's cart."""
        user = DATA_REPOSITORY["users"].get(username)

        # Role-based access control - only user with a 'customer' Role can add to cart
        if user and user["role"].lower() != "customer":
            logging.warning(f"Access denied: {username} (role: {user['role']}) attempted to add to cart.")
            print("Access denied: Only customers can add items to the cart.")
            return

        user_cart = user.setdefault("cart", {})
        for item in DATA_REPOSITORY["items"]:
            if item["item_id"] == item_id:
                if item_id in user_cart:
                    user_cart[item_id]["count"] += 1
                    user_cart[item_id]["total_cost"] += item["price"]
                else:
                    user_cart[item_id] = {
                        "name": item["name"],
                        "category": item["category"],
                        "price": item["price"],
                        "count": 1,
                        "total_cost": item["price"]
                    }
                logging.info(f"Item {item['name']} added to cart for user {username}.") #Logging the Add to Cart event
                print(f"Item {item['name']} added to cart.")
                return
        print("Item not found.")


    @staticmethod
    def remove_from_cart(username: str, item_id: int):
        """Remove an item from the user's cart."""
        user_cart = DATA_REPOSITORY["users"][username].get("cart", {})
        if item_id in user_cart:
            user_cart[item_id]["count"] -= 1
            user_cart[item_id]["total_cost"] -= user_cart[item_id]["price"]
            if user_cart[item_id]["count"] <= 0:
                del user_cart[item_id]
                print("Item removed completely from the cart.")
            else:
                print(f"One unit of {user_cart[item_id]['name']} removed from cart.")
        else:
            print("Item not found in cart.")

    @staticmethod
    def view_cart(username: str):
        """View all items in the user's cart."""
        user_cart = DATA_REPOSITORY["users"][username].get("cart", {})
        if not user_cart:
            print("Cart is empty.")
        else:
            print("Items in your cart:")
            for item_id, details in user_cart.items():
                print(f"ID: {item_id}, Name: {details['name']}, "
                      f"Category: {details['category']}, Price: {details['price']:.2f}, "
                      f"Count: {details['count']}, Total Cost: {details['total_cost']:.2f}")

    @staticmethod
    def purchase(username: str):
        """Simulate purchasing items in the cart."""
        user_cart = DATA_REPOSITORY["users"][username].get("cart", {})
        if not user_cart:
            print("Cart is empty.")
        else:
            total = sum(details["total_cost"] for details in user_cart.values())
            print(f"Purchase successful! Total amount: ${total:.2f}")
            DATA_REPOSITORY["users"][username]["cart"] = {} #Reset the cart for a user after his purchase


# CRUD Operations for admin
class AdminCRUD:
    @staticmethod
    def create_user(username: str, password: str, company_id: str, first_name: str, last_name: str, role: str):
        """Admin creates a new user with additional fields."""
        caller = DATA_REPOSITORY["users"].get(username)

        # Role-based access control - only admins should be able to create users
        if caller and caller["role"].lower() != "admin":
            logging.warning(f"Access denied: {username} (role: {caller['role']}) attempted to create a user.")
            print("Access denied: Only admins can create new users.")
            return

        # Validate first name and last name - should only include letters
        if not re.match(r"^[A-Za-z]+$", first_name):
            logging.error(f"Invalid first name: {first_name}. Only letters are allowed.")
            print("Error: First name should only contain letters.")
            return

        if not re.match(r"^[A-Za-z]+$", last_name):
            logging.error(f"Invalid last name: {last_name}. Only letters are allowed.")
            print("Error: Last name should only contain letters.")
            return

        # Validate password - at least 6 characters with at least one letter and one number
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$", password):
            logging.error(f"Invalid password provided for new user {username}.")
            print("Error: Password must be at least 6 characters long, contain at least one letter and one number.")
            return

        # Proceed with user creation
        user = {
            "password": hash_password(password),
            "company_id": company_id,
            "first_name": first_name,
            "last_name": last_name,
            "role": role
        }
        DATA_REPOSITORY["users"][username] = user
        logging.info(f"User {username} created by admin.") # log the event
        print(f"User {username} created successfully!")


    @staticmethod
    def edit_user(username: str, new_data: dict):
        """Admin edits an existing user."""
        user = DATA_REPOSITORY["users"].get(username)
        if user:
            user.update(new_data)
            print(f"User {username} updated successfully.")
        else:
            print("User not found.")


    @staticmethod
    def delete_user(username: str):
        """Admin deletes a user."""
        if username in DATA_REPOSITORY["users"]:
            del DATA_REPOSITORY["users"][username]
            print(f"User {username} deleted successfully.")
        else:
            print("User not found.")


class CRUDOperations:
    @staticmethod
    def create_item(item_name: str, category: str, price: float):
        """Add a new item to the inventory."""
        new_item = {
            "item_id": len(DATA_REPOSITORY["items"]) + 1,
            "name": item_name,
            "category": category,
            "price": price
        }
        DATA_REPOSITORY["items"].append(new_item)
        print(f"Item {item_name} added to inventory.")

    @staticmethod
    def read_items():
        """List all items in the inventory."""
        print("Items in Inventory:")
        for item in DATA_REPOSITORY["items"]:
            print(f"ID: {item['item_id']}, Name: {item['name']}, Category: {item['category']}, Price: {item['price']}")

    @staticmethod
    def update_item(item_id: int, name=None, category=None, price=None):
        """Update an existing item in the inventory."""
        for item in DATA_REPOSITORY["items"]:
            if item["item_id"] == item_id:
                if name:
                    item["name"] = name
                if category:
                    item["category"] = category
                if price:
                    item["price"] = price
                print(f"Item ID {item_id} updated.")
                return
        print(f"Item ID {item_id} not found.")

    @staticmethod
    def delete_item(item_id: int):
        """Remove an item from the inventory."""
        for item in DATA_REPOSITORY["items"]:
            if item["item_id"] == item_id:
                DATA_REPOSITORY["items"].remove(item)
                print(f"Item ID {item_id} deleted.")
                return
        print(f"Item ID {item_id} not found.")



# UI Class - this is what user interacts with and all other functions from various classes are called here
class AppUI:
    @staticmethod
    def main():
        global SECURITY_ENABLED  

        # Prompt user to choose security mode
        while SECURITY_ENABLED is None:
            security_choice = input("Choose App mode: 'Secure' or 'Insecure': ").strip().lower()
            if security_choice == "secure":
                SECURITY_ENABLED = True
                print("App is running in Secure Mode.")
            elif security_choice == "insecure":
                SECURITY_ENABLED = False
                print("App is running in Insecure Mode.")
            else:
                print("Invalid choice. Please type 'Secure' or 'Insecure'.")

        while True:
            user_type = input("Enter your role (Admin, Clerk, Customer, Hacker) or 'Exit': ").strip().lower()
            if user_type == "admin":
                AppUI.admin_flow()
            elif user_type == "clerk":
                AppUI.clerk_flow()
            elif user_type == "customer":
                AppUI.customer_flow()
            elif user_type == "hacker":
                AppUI.hacker_flow()
            elif user_type == "exit":
                print("Exiting the application.")
                break
            else:
                print("Invalid input. Please try again.")


    @staticmethod
    def admin_flow():
        username = input("Admin username: ")
        password = input("Password: ")
        otp = MultiFactorAuthentication.send_otp()
        input_otp = input("Enter the OTP sent to your registered email: ").strip()

        if Authentication.login(username, password) and MultiFactorAuthentication.verify_otp(input_otp, otp):
            # Persist Session Token for the user's session in the repository
            save_repository()
            while True:
                choice = input("Options: Create User, Edit User, View User, Delete User, Log Out: ").strip().lower()
                if choice == "log out":
                    Authentication.logout(username)
                    # Delete Session Token for the user's session in the repository - simulate session storing for tracking
                    save_repository()
                    break                    
                elif choice == "create user":
                    new_username = input("Enter new username: ")
                    new_password = input("Enter new password: ")
                    company_id = input("Enter company ID: ")
                    first_name = input("Enter first name: ")
                    last_name = input("Enter last name: ")
                    role = input("Enter role (Admin, Clerk, Customer): ")

                    # Add the new company ID directly to the repository if it's not already present
                    if company_id not in DATA_REPOSITORY["company_ids"]:
                        DATA_REPOSITORY["company_ids"].append(company_id)

                    # Create and save the new user
                    AdminCRUD.create_user(new_username, new_password, company_id, first_name, last_name, role)

                    # Persist changes in the repository
                    save_repository()

                elif choice == "edit user":
                    edit_username = input("Enter username to edit: ")
                    new_data = {}
                    new_password = input("Enter new password (leave blank to skip): ").strip()
                    new_company_id = input("Enter new company ID (leave blank to skip): ").strip()
                    new_first_name = input("Enter new first name (leave blank to skip): ").strip()
                    new_last_name = input("Enter new last name (leave blank to skip): ").strip()
                    new_role = input("Enter new role (leave blank to skip): ").strip()

                    if new_password:
                        new_data["password"] = hash_password(new_password)
                    if new_company_id:
                        new_data["company_id"] = new_company_id
                    if new_first_name:
                        new_data["first_name"] = new_first_name
                    if new_last_name:
                        new_data["last_name"] = new_last_name
                    if new_role:
                        new_data["role"] = new_role

                    AdminCRUD.edit_user(edit_username, new_data)

                    # Persist changes in the repository
                    save_repository()

                elif choice == "view user":
                    print("Current users in the system:")
                    for user, details in DATA_REPOSITORY["users"].items():
                        print(f"Username: {user}, First Name: {details['first_name']}, Last Name: {details['last_name']}, Role: {details['role']}, Company ID: {details['company_id']}")
                elif choice == "delete user":
                    delete_username = input("Enter username to delete: ")
                    AdminCRUD.delete_user(delete_username)
                    # Persist changes in the repository
                    save_repository()
                else:
                    print("Invalid choice. Please try again.")
        else:
            print("Authentication failed.")


    @staticmethod
    def clerk_flow():
        username = input("Clerk username: ")
        password = input("Password: ")
        otp = MultiFactorAuthentication.send_otp()
        input_otp = input("Enter the OTP sent to your registered email: ").strip()

        if Authentication.login(username, password) and MultiFactorAuthentication.verify_otp(input_otp, otp):
            # Persist Session Token for the user's session in the repository
            save_repository()
            while True:
                choice = input("Options: Create Item, Update Item, Delete Item, Read Items, Log Out: ").strip().lower()
                if choice == "log out":
                    Authentication.logout(username)
                    # Persist Session Token for the user's session in the repository
                    save_repository()
                    break
                elif choice == "create item":
                    item_name = input("Enter item name: ")
                    category = input("Enter item category: ")
                    price = float(input("Enter item price: "))
                    CRUDOperations.create_item(item_name, category, price)
                    # Persist changes to the JSON file repo
                    save_repository()
                elif choice == "update item":
                    item_id = int(input("Enter item ID to update: "))
                    new_name = input("Enter new name (leave blank to skip): ").strip()
                    new_category = input("Enter new category (leave blank to skip): ").strip()
                    new_price = input("Enter new price (leave blank to skip): ").strip()
                    CRUDOperations.update_item(item_id, new_name or None, new_category or None, float(new_price) if new_price else None)
                    # Persist changes to the JSON file repo
                    save_repository()
                elif choice == "delete item":
                    item_id = int(input("Enter item ID to delete: "))
                    CRUDOperations.delete_item(item_id)
                    # Persist changes to the JSON file repo
                    save_repository()
                elif choice == "read items":
                    CRUDOperations.read_items()
                else:
                    print("Invalid choice. Please try again.")
        else:
            print("Authentication failed.")


    @staticmethod
    def customer_flow():
        username = input("Customer username: ")
        password = input("Password: ")
        company_id = input("Company ID: ")  # Ask for Company ID
        otp = MultiFactorAuthentication.send_otp()
        input_otp = input("Enter the OTP sent to your registered email: ").strip()

        # Use Flask API to verify company ID
        response = requests.post(
            "http://127.0.0.1:5000/verify_company_id",
            json={"username": username, "company_id": company_id}
        )

        if response.status_code != 200:
            print("Company ID verification failed. Access denied.")
            return

        # Authenticate the user
        if Authentication.login(username, password) and MultiFactorAuthentication.verify_otp(input_otp, otp):
            save_repository()  # Persist session
            while True:
                choice = input(
                    "Options: View Items, View Cart, Add to Cart, Remove from Cart, Purchase, Update Info, Request Deletion, Log Out: "
                ).strip().lower()
                if choice == "log out":
                    Authentication.logout(username)
                    save_repository()
                    break
                elif choice == "view items":
                    CRUDOperations.read_items()  # Call to list all items
                elif choice == "view cart":
                    CartOperations.view_cart(username)
                elif choice == "add to cart":
                    item_id = int(input("Enter item ID to add to cart: "))
                    CartOperations.add_to_cart(username, item_id)                    
                    # Update user's cart in repo
                    save_repository()
                elif choice == "remove from cart":
                    item_id = int(input("Enter item ID to remove from cart: "))
                    CartOperations.remove_from_cart(username, item_id)
                    # Update user's cart in repo
                    save_repository()
                elif choice == "purchase":
                    CartOperations.purchase(username)
                    # Empty user's cart and update repo
                    save_repository()
                elif choice == "update info":
                    # Allow customer to update their details
                    new_password = input("Enter new password (leave blank to skip): ").strip()
                    new_first_name = input("Enter new first name (leave blank to skip): ").strip()
                    new_last_name = input("Enter new last name (leave blank to skip): ").strip()

                    if new_password:
                        DATA_REPOSITORY["users"][username]["password"] = hash_password(new_password)
                    if new_first_name:
                        DATA_REPOSITORY["users"][username]["first_name"] = new_first_name
                    if new_last_name:
                        DATA_REPOSITORY["users"][username]["last_name"] = new_last_name

                    save_repository()  # Persist changes
                    print("Profile updated successfully.")
                elif choice == "request deletion":
                    del DATA_REPOSITORY["users"][username]
                    Authentication.logout(username)
                    print("Account deleted and logged out. Exiting...")
                    save_repository()
                    break
                else:
                    print("Invalid choice. Please try again.")
        else:
            print("Authentication failed.")


    @staticmethod
    def hacker_flow():
        print("Hacker options:")
        print("1. Brute Force Attack")
        print("2. Denial of Service (DoS) Attack")
        print("3. API Injection Attack")
        choice = input("Choose an attack type: ").strip()
        if choice == "1":
            username = input("Enter username to target: ")
            Hacker.brute_force_attack(username)
        elif choice == "2":
            Hacker.denial_of_service()
        elif choice == "3":
            Hacker.api_injection_attack()
        else:
            print("Invalid choice. Returning to main menu.")


if __name__ == "__main__":
    # Start Flask server in a separate thread. 
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    print("Launching application interface")
    # In parallel starting Flask API server for company ID verification. 
    # It needs to start early to ensure that it can respond to any requests made during the application's execution.
    try:
        AppUI.main()  # Run the main application interface
    finally:
        # Signal the Flask thread to stop and wait for it to finish. Trigger the stop_event defined in the beginning of code.
        stop_event.set()
        flask_thread.join()
        print("Application has been terminated.")
