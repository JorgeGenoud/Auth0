import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"

# You must set these in your .env or export them before running
USERNAME = os.getenv("TEST_USERNAME")
PASSWORD = os.getenv("TEST_PASSWORD")

def test_login_and_protected_route():
    if not USERNAME or not PASSWORD:
        print("Skipping test: TEST_USERNAME and TEST_PASSWORD env vars not set.")
        return

    print(f"Attempting login for user: {USERNAME}")
    
    # 1. Login
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=login_payload)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Login Failed: {response.text}")
            return
            
        data = response.json()
        access_token = data.get("access_token")
        print(f"Access Token retrieved: {access_token[:20]}...")
        
        # 2. Access Protected Route
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        # Using /users endpoint which requires auth
        users_url = f"{BASE_URL}/users?per_page=1"
        print(f"Accessing protected route: {users_url}")
        
        response = requests.get(users_url, headers=headers)
        print(f"Protected Route Status: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Authenticated and accessed protected route!")
            print(f"Response: {response.json()}")
        else:
            print(f"FAILED: Could not access protected route. {response.text}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_login_and_protected_route()
