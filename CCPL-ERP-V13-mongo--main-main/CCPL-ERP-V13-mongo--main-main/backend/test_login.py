import requests
import json

# Test login
url = "http://localhost:8000/api/auth/login"
payload = {
    "email": "demo@example.com",
    "password": "Demo123!"
}

headers = {
    "Content-Type": "application/json"
}

print("Testing login...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        print("\n✅ Login successful!")
        print(f"Access Token: {response.json()['access_token'][:50]}...")
    else:
        print("\n❌ Login failed!")

except Exception as e:
    print(f"\n❌ Error: {e}")
