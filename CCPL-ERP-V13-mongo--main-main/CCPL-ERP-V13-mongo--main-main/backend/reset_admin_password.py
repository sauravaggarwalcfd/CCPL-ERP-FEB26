#!/usr/bin/env python3
"""
Reset admin password to a known value
Usage: python reset_admin_password.py
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def reset_password():
    mongodb_url = os.getenv('MONGODB_URL')
    db_name = os.getenv('DATABASE_NAME', 'inventory_erp')

    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]

    # New password
    new_password = "Admin@123"
    new_hash = pwd_context.hash(new_password)

    print("=" * 60)
    print("Admin Password Reset Tool")
    print("=" * 60)
    print()

    # Find all admin/super-admin users
    admin_users = await db.users.find({
        "$or": [
            {"email": {"$regex": "admin", "$options": "i"}},
            {"role.slug": {"$in": ["admin", "super-admin"]}}
        ]
    }).to_list(length=10)

    if not admin_users:
        print("No admin users found!")
        print("\nSearching for any users...")
        all_users = await db.users.find().to_list(length=10)
        if all_users:
            print(f"\nFound {len(all_users)} users:")
            for user in all_users:
                print(f"  - {user.get('email')} ({user.get('role', {}).get('name', 'No role')})")
            admin_users = all_users
        else:
            print("No users found in database!")
            client.close()
            return

    print(f"Found {len(admin_users)} admin user(s):\n")

    for user in admin_users:
        email = user.get('email')
        name = user.get('full_name')
        role = user.get('role', {})

        print(f"Email: {email}")
        print(f"Name: {name}")
        print(f"Role: {role.get('name', 'Unknown')}")

        # Update password
        result = await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"password_hash": new_hash}}
        )

        if result.modified_count > 0:
            print(f"✓ Password updated successfully!")
        else:
            print(f"✗ Password update failed")
        print()

    print("=" * 60)
    print("Password Reset Complete!")
    print("=" * 60)
    print()
    print("New Login Credentials:")
    print(f"  Email:    {admin_users[0].get('email')}")
    print(f"  Password: {new_password}")
    print()

    client.close()

if __name__ == "__main__":
    asyncio.run(reset_password())
