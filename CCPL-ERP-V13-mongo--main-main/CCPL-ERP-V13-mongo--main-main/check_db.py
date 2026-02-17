#!/usr/bin/env python3
"""Check what's in MongoDB"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_database():
    print("=" * 60)
    print("CHECKING MONGODB CONTENTS")
    print("=" * 60)
    
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "inventory_erp")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # List all collections
    print("\n📂 Collections in 'inventory_erp' database:")
    collections = await db.list_collection_names()
    for col in collections:
        count = await db[col].count_documents({})
        print(f"   - {col}: {count} documents")
    
    # Check user collection specifically
    if "user" in collections:
        print("\n👤 User collection:")
        users = await db["user"].find({}).to_list(10)
        for user in users:
            print(f"   - {user.get('email', 'Unknown')} (Status: {user.get('status', 'Unknown')})")
    else:
        print("\n❌ 'user' collection does not exist!")
        print("   Need to create demo user first")
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_database())
