#!/usr/bin/env python3
"""Test API login using urllib"""
import urllib.request
import urllib.error
import json
import time

def test_login():
    print("=" * 70)
    print("TESTING LOGIN API ENDPOINT")
    print("=" * 70)
    
    url = "http://localhost:8000/api/auth/login"
    payload = {
        "email": "demo@example.com",
        "password": "Demo123!"
    }
    
    print(f"\n🔑 Endpoint: POST {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.status
            response_data = json.loads(response.read().decode('utf-8'))
            
            print(f"✅ STATUS CODE: {status_code}\n")
            print("📋 RESPONSE:")
            print(f"   Access Token: {response_data.get('access_token', 'N/A')[:50]}...")
            print(f"   Refresh Token: {response_data.get('refresh_token', 'N/A')[:50]}...")
            print(f"   Token Type: {response_data.get('token_type', 'N/A')}")
            print(f"   Expires In: {response_data.get('expires_in', 'N/A')} seconds")
            
            user = response_data.get('user', {})
            print(f"\n👤 USER INFO:")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Full Name: {user.get('full_name', 'N/A')}")
            print(f"   Status: {user.get('status', 'N/A')}")
            print(f"   ID: {user.get('id', 'N/A')}")
            
            print(f"\n✅ LOGIN SUCCESSFUL!")
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR: {e.code}")
        response_data = json.loads(e.read().decode('utf-8'))
        print(f"   Detail: {response_data.get('detail', 'No details provided')}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    print("Waiting 2 seconds for backend to be ready...")
    time.sleep(2)
    test_login()
