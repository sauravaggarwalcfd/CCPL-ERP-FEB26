#!/usr/bin/env python3
"""Test password verification"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bcrypt import checkpw

async def test_password():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "inventory_erp")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Get the user
    user = await db["users"].find_one({"email": "demo@example.com"})
    
    if user:
        print("Testing password verification:")
        print(f"Email: {user.get('email')}")
        print(f"Stored Hash: {user.get('password_hash')[:50]}...\n")
        
        password_to_test = "Demo123!"
        stored_hash = user.get('password_hash')
        
        # The hash is already a string, convert to bytes for checkpw
        if isinstance(stored_hash, str):
            stored_hash_bytes = stored_hash.encode('utf-8')
        else:
            stored_hash_bytes = stored_hash
        
        password_bytes = password_to_test.encode('utf-8')
        
        print(f"Testing password: '{password_to_test}'")
        print(f"Hash bytes type: {type(stored_hash_bytes)}")
        print(f"Password bytes type: {type(password_bytes)}")
        
        is_valid = checkpw(password_bytes, stored_hash_bytes)
        
        if is_valid:
            print(f"\n✅ PASSWORD VERIFICATION SUCCESSFUL!")
        else:
            print(f"\n❌ PASSWORD VERIFICATION FAILED!")
            print("\nTrying different hashing approaches...")
            
            # Test if it's a plaintext password stored (wrong!)
            if stored_hash == password_to_test:
                print("   Warning: Password is stored as plaintext!")
    else:
        print("User not found!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_password())
