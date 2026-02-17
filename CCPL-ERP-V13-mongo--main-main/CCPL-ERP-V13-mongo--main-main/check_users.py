#!/usr/bin/env python3
"""Check user in users collection"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_users():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "inventory_erp")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("📊 Users in database:")
    users = await db["users"].find({}).to_list(10)
    for user in users:
        print(f"\n   Email: {user.get('email')}")
        print(f"   Full Name: {user.get('full_name')}")
        print(f"   Status: {user.get('status')}")
        print(f"   Password Hash: {user.get('password_hash', 'N/A')[:50]}...")
    
    if not users:
        print("   (No users found)")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
