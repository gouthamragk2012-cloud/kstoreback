import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_register():
    print("Testing user registration...")
    data = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}\n")
    return result.get('data', {}).get('access_token')

def test_login():
    print("Testing login...")
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}\n")
    return result.get('data', {}).get('access_token')

def test_get_current_user(token):
    print("Testing get current user...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_get_products():
    print("Testing get products...")
    response = requests.get(f"{BASE_URL}/products")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_get_categories():
    print("Testing get categories...")
    response = requests.get(f"{BASE_URL}/categories")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("API Testing Script")
    print("=" * 50 + "\n")
    
    try:
        test_health()
        
        # Try to register (might fail if user exists)
        token = test_register()
        
        # If registration fails, try login
        if not token:
            token = test_login()
        
        if token:
            test_get_current_user(token)
        
        test_get_products()
        test_get_categories()
        
        print("=" * 50)
        print("Testing completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
