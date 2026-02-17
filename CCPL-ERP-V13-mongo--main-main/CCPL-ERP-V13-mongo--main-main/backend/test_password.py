import asyncio
from app.models.user import User
from app.core.security import verify_password, get_password_hash
from app.database import connect_to_mongo, close_mongo_connection

async def test():
    await connect_to_mongo()
    
    user = await User.find_one(User.email == "demo@example.com")
    if user:
        print(f"✓ User found: {user.email}")
        print(f"✓ Password hash exists: {bool(user.password_hash)}")
        print(f"✓ Password hash length: {len(user.password_hash)}")
        
        # Try to verify password
        try:
            result = verify_password("Demo123!", user.password_hash)
            print(f"✓ Password verification result: {result}")
            if result:
                print("✓✓✓ PASSWORD IS CORRECT ✓✓✓")
            else:
                print("✗✗✗ PASSWORD IS INCORRECT ✗✗✗")
        except Exception as e:
            print(f"✗ Error during verification: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ User not found")
    
    await close_mongo_connection()

asyncio.run(test())
