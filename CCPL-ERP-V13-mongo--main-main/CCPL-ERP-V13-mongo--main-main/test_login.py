#!/usr/bin/env python3
"""Test login endpoint"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.app.database import connect_to_mongo, close_mongo_connection
from backend.app.models.user import User
from backend.app.core.security import verify_password, get_password_hash
from datetime import datetime
import httpx

async def test_login():
    print("=" * 60)
    print("TESTING LOGIN SYSTEM")
    print("=" * 60)
    
    # Step 1: Connect to MongoDB
    print("\n1️⃣  Connecting to MongoDB...")
    try:
        await connect_to_mongo()
        print("   ✅ Connected to MongoDB")
    except Exception as e:
        print(f"   ❌ MongoDB connection failed: {e}")
        return
    
    # Step 2: Check if demo user exists in database
    print("\n2️⃣  Checking for demo user in database...")
    try:
        demo_user = await User.find_one(User.email == "demo@example.com")
        if demo_user:
            print(f"   ✅ Demo user found")
            print(f"      Email: {demo_user.email}")
            print(f"      Status: {demo_user.status}")
            print(f"      Password Hash Length: {len(demo_user.password_hash)}")
            
            # Test password verification
            print("\n3️⃣  Testing password verification...")
            is_valid = verify_password("Demo123!", demo_user.password_hash)
            if is_valid:
                print("   ✅ Password verification SUCCESSFUL")
            else:
                print("   ❌ Password verification FAILED")
                print("      This is the root cause!")
        else:
            print("   ❌ Demo user NOT found in database")
            print("      Please run: py backend/create_demo_user.py")
            return
    except Exception as e:
        print(f"   ❌ Error checking user: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Test API endpoint
    print("\n4️⃣  Testing API login endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/auth/login",
                json={"email": "demo@example.com", "password": "Demo123!"},
                timeout=10.0
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✅ LOGIN SUCCESSFUL!")
                print(f"      Access Token: {data.get('access_token', 'N/A')[:50]}...")
                print(f"      Token Type: {data.get('token_type', 'N/A')}")
                print(f"      Expires In: {data.get('expires_in', 'N/A')} seconds")
                print(f"      User: {data.get('user', {}).get('email', 'N/A')}")
            else:
                print(f"   ❌ LOGIN FAILED")
                print(f"      Response: {response.text}")
    except Exception as e:
        print(f"   ❌ API request error: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    print("\n5️⃣  Closing connections...")
    try:
        await close_mongo_connection()
        print("   ✅ Database connection closed")
    except Exception as e:
        print(f"   ⚠️  Error closing connection: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_login())
