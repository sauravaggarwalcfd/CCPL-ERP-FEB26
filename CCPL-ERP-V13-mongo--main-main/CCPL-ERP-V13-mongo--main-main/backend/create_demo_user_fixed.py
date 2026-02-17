import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User, UserStatus
from datetime import datetime
from passlib.context import CryptContext

# Use argon2 instead of bcrypt (more reliable)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def setup_demo_user():
    try:
        await connect_to_mongo()
        print("✓ Connected to MongoDB")
        
        # Check if demo user exists
        demo_user = await User.find_one(User.email == "demo@example.com")
        
        if demo_user:
            print(f"✓ Demo user already exists: {demo_user.email}")
            print(f"  Status: {demo_user.status}")
            print(f"  Created: {demo_user.created_at}")
        else:
            print("✗ Demo user not found, creating one...")
            
            # Create demo user with passlib hashing (correct method)
            password = "Demo123!"
            password_hash = pwd_context.hash(password)
            
            new_user = User(
                full_name="Demo User",
                email="demo@example.com",
                password_hash=password_hash,
                status=UserStatus.ACTIVE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            
            await new_user.save()
            print(f"✓ Demo user created successfully!")
            print(f"  Email: demo@example.com")
            print(f"  Password: Demo123!")
        
        # List all users
        all_users = await User.find_all().to_list(100)
        
        print(f"\nTotal users in database: {len(all_users)}")
        for user in all_users:
            print(f"  - {user.email} (Status: {user.status})")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(setup_demo_user())
