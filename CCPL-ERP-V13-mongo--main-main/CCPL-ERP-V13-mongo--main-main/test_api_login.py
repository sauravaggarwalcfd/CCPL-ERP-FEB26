#!/usr/bin/env python3
"""Test the API login endpoint"""
import httpx
import asyncio
import json

async def test_api_login():
    print("=" * 70)
    print("TESTING API LOGIN ENDPOINT")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        print("\n🔑 Testing: POST /api/auth/login")
        print("Credentials:")
        print("  Email: demo@example.com")
        print("  Password: Demo123!")
        
        try:
            response = await client.post(
                "http://localhost:8000/api/auth/login",
                json={
                    "email": "demo@example.com",
                    "password": "Demo123!"
                },
                timeout=10.0
            )
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ LOGIN SUCCESSFUL!")
                print(f"\n📋 Response Data:")
                print(f"   Access Token: {data.get('access_token', 'N/A')[:60]}...")
                print(f"   Refresh Token: {data.get('refresh_token', 'N/A')[:60]}...")
                print(f"   Token Type: {data.get('token_type', 'N/A')}")
                print(f"   Expires In: {data.get('expires_in', 'N/A')} seconds")
                
                user = data.get('user', {})
                print(f"\n👤 User Info:")
                print(f"   Email: {user.get('email', 'N/A')}")
                print(f"   Full Name: {user.get('full_name', 'N/A')}")
                print(f"   Status: {user.get('status', 'N/A')}")
            else:
                print(f"\n❌ LOGIN FAILED!")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(test_api_login())
