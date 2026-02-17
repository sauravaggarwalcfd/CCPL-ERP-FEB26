#!/usr/bin/env python3
"""Simple direct MongoDB test of login"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bcrypt import checkpw

async def test_login_direct():
    print("=" * 60)
    print("DIRECT MONGODB LOGIN TEST")
    print("=" * 60)
    
    # Connect to MongoDB (uses env if set)
    print("\n1️⃣  Connecting to MongoDB...")
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "inventory_erp")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    users_collection = db["user"]
    
    # Find the demo user
    print("\n2️⃣  Searching for demo user...")
    user = await users_collection.find_one({"email": "demo@example.com"})
    
    if user:
        print("   ✅ Demo user found!")
        print(f"      Email: {user.get('email')}")
        print(f"      Full Name: {user.get('full_name')}")
        print(f"      Status: {user.get('status')}")
        print(f"      Password Hash: {user.get('password_hash')[:50]}...")
        
        # Test password verification
        print("\n3️⃣  Testing password verification...")
        password_to_test = "Demo123!"
        stored_hash = user.get('password_hash').encode() if isinstance(user.get('password_hash'), str) else user.get('password_hash')
        password_bytes = password_to_test.encode()
        
        is_valid = checkpw(password_bytes, stored_hash)
        
        if is_valid:
            print(f"   ✅ PASSWORD VERIFICATION SUCCESSFUL!")
            print(f"      Password '{password_to_test}' matches the stored hash")
        else:
            print(f"   ❌ PASSWORD VERIFICATION FAILED!")
            print(f"      Password '{password_to_test}' does NOT match the stored hash")
            
            # Try to recreate with the password
            print("\n   🔧 Attempting to recreate password hash...")
            from bcrypt import hashpw, gensalt
            new_hash = hashpw(password_bytes, gensalt(rounds=12)).decode()
            print(f"      Old hash: {user.get('password_hash')[:50]}...")
            print(f"      New hash: {new_hash[:50]}...")
            
            # Test if new hash works
            is_new_valid = checkpw(password_bytes, new_hash.encode())
            if is_new_valid:
                print(f"   ✅ New hash verification works!")
                # Update the user with new hash
                await users_collection.update_one(
                    {"email": "demo@example.com"},
                    {"$set": {"password_hash": new_hash}}
                )
                print(f"   ✅ Updated user in database with correct hash")
    else:
        print("   ❌ Demo user NOT found!")
        print("      Run: py backend/create_demo_user.py")
    
    # Close connection
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_login_direct())
