import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User, UserStatus
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def create_simple_user():
    try:
        await connect_to_mongo()
        print("✓ Connected to MongoDB")

        # Delete if exists
        existing = await User.find_one(User.email == "test@test.com")
        if existing:
            await existing.delete()
            print("✓ Deleted existing test user")

        # Create test user with simple password
        password = "test1234"
        password_hash = pwd_context.hash(password)

        new_user = User(
            full_name="Test User",
            email="test@test.com",
            password_hash=password_hash,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        await new_user.save()
        print(f"✓ Simple test user created successfully!")
        print(f"  Email: test@test.com")
        print(f"  Password: test1234")
        print(f"\nUse these credentials to test login.")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_simple_user())
