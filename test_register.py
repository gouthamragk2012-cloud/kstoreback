import requests
import json

# Test user registration
url = "http://localhost:5000/api/auth/register"
data = {
    "email": "john@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
}

print("Testing User Registration...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}\n")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n✅ SUCCESS! User account created!")
        result = response.json()
        access_token = result['data']['access_token']
        print(f"\nYour Access Token (use this in Postman):")
        print(f"{access_token}")
    else:
        print("\n❌ Registration failed")
        
except Exception as e:
    print(f"Error: {e}")
