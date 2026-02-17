# 🔐 Login Troubleshooting Guide

## ✅ Backend is Working!

I've verified that the backend login API is working correctly:

```bash
✅ Login API tested successfully
✅ Demo user exists and is active
✅ Password authentication working
✅ Tokens being generated correctly
```

---

## 🔍 Troubleshooting Steps

### Step 1: Check Browser Console

1. **Open the application**: http://localhost:5173
2. **Open Developer Tools**:
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I`
   - Firefox: Press `F12` or `Ctrl+Shift+K`
3. **Go to the Console tab**
4. **Try to login** with:
   - Email: `demo@example.com`
   - Password: `Demo123!`
5. **Look for error messages** in the console

**Common errors and solutions:**

#### Error: "Network Error" or "Failed to fetch"
- **Cause**: Frontend can't reach backend
- **Solution**:
  ```bash
  # Verify backend is running:
  curl http://localhost:8000
  # Should return: {"message":"Inventory ERP API","version":"1.0.0"}
  ```

#### Error: "CORS policy"
- **Cause**: CORS not properly configured
- **Solution**: Already configured correctly, but verify:
  ```bash
  # Backend should allow localhost:5173
  # Check backend/app/main.py CORS settings
  ```

#### Error: 401 or 403
- **Cause**: Invalid credentials
- **Solution**: Make sure you're using exactly:
  - Email: `demo@example.com` (lowercase)
  - Password: `Demo123!` (exact case, with exclamation mark)

#### Error: 422 Unprocessable Entity
- **Cause**: Invalid data format
- **Solution**: Check if email is in correct format

---

### Step 2: Test Backend Directly

Open a new terminal and test the login API directly:

```bash
cd /workspaces/CCPL-ERP-V13-mongo-/backend
python test_login.py
```

**Expected Output:**
```
✅ Login successful!
Access Token: eyJhbGc...
```

If this works, the backend is fine and the issue is in the frontend.

---

### Step 3: Check Network Tab

1. **Open Developer Tools** (F12)
2. **Go to Network tab**
3. **Try to login**
4. **Look for the request to** `/api/auth/login`
5. **Click on it** to see details

**What to check:**
- **Request URL**: Should be `http://localhost:8000/api/auth/login`
- **Request Method**: Should be `POST`
- **Request Payload**: Should show email and password
- **Response**: Check status code and error message

---

### Step 4: Verify Credentials

Double-check you're using the correct credentials:

```
Email:    demo@example.com
Password: Demo123!
```

**Important:**
- Email must be lowercase
- Password is case-sensitive
- Password has an exclamation mark at the end

---

### Step 5: Clear Browser Cache

Sometimes old cached data can cause issues:

1. **Open Developer Tools** (F12)
2. **Right-click on refresh button**
3. **Select "Empty Cache and Hard Reload"**
4. **Try logging in again**

Or use incognito/private browsing mode to test.

---

### Step 6: Check Frontend API Configuration

Verify the frontend is pointing to the correct backend:

```bash
# Check the API URL configuration:
grep -n "API_BASE_URL\|VITE_API_URL" /workspaces/CCPL-ERP-V13-mongo-/frontend/src/services/api.js
```

**Expected:**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
```

This should default to `http://localhost:8000/api` which is correct.

---

### Step 7: Restart Frontend

Sometimes the frontend dev server needs a restart:

```bash
# Kill the frontend process
lsof -ti:5173 | xargs kill -9

# Restart frontend
cd /workspaces/CCPL-ERP-V13-mongo-/frontend
npm run dev
```

Then try logging in again.

---

### Step 8: Check for Password Manager Interference

Some password managers auto-fill incorrectly:

1. **Clear the login form**
2. **Manually type** the credentials (don't paste)
3. **Don't let password manager auto-fill**
4. **Try logging in**

---

## 🔄 Quick Fixes

### Fix 1: Recreate Demo User

If the user might be corrupted:

```bash
cd /workspaces/CCPL-ERP-V13-mongo-/backend
python create_demo_user_fixed.py
```

### Fix 2: Test with Simpler Password

Create a user with a simpler password to test:

```bash
cd /workspaces/CCPL-ERP-V13-mongo-/backend
python -c "
import asyncio
from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User, UserStatus
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

async def create_test_user():
    await connect_to_mongo()

    # Delete if exists
    existing = await User.find_one(User.email == 'test@example.com')
    if existing:
        await existing.delete()

    # Create with simple password
    password_hash = pwd_context.hash('Test1234')
    new_user = User(
        full_name='Test User',
        email='test@example.com',
        password_hash=password_hash,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await new_user.save()
    print('✅ Test user created: test@example.com / Test1234')

    await close_mongo_connection()

asyncio.run(create_test_user())
"
```

Then try logging in with:
- Email: `test@example.com`
- Password: `Test1234`

---

## 📋 What Error Are You Seeing?

Please provide the exact error message you're seeing. It could be:

1. **"Invalid credentials"** - Wrong email/password
2. **"Network error"** - Can't reach backend
3. **"User is locked"** - Too many failed attempts
4. **"User is inactive"** - User account disabled
5. **Other error** - Check browser console for details

---

## 🧪 Test Results

I've already tested:

✅ Backend API is running (port 8000)
✅ Frontend is running (port 5173)
✅ MongoDB is connected
✅ Demo user exists and is active
✅ Login API works correctly (tested with Python)
✅ CORS is properly configured
✅ Password hashing is working
✅ Token generation is working

**The backend authentication system is 100% functional.**

---

## 💡 Most Likely Causes

Based on the tests, the most likely issues are:

1. **Browser cache** - Clear cache and try again
2. **Typo in credentials** - Make sure email is lowercase and password is exact
3. **Browser extension interference** - Try in incognito mode
4. **Password manager auto-fill** - Manually type credentials
5. **Console error** - Check browser console for specific error

---

## 🆘 If Still Having Issues

1. **Open browser console** (F12)
2. **Screenshot the error** in the Console tab
3. **Screenshot the error** in the Network tab (for /api/auth/login request)
4. **Tell me the exact error message** you see on the screen

This will help me identify the specific issue and provide a targeted fix.

---

## 📞 Quick Commands

```bash
# Check backend is running
curl http://localhost:8000

# Check frontend is running
curl http://localhost:5173

# Test login API
cd /workspaces/CCPL-ERP-V13-mongo-/backend
python test_login.py

# Recreate demo user
python create_demo_user_fixed.py

# Restart frontend
lsof -ti:5173 | xargs kill -9
cd /workspaces/CCPL-ERP-V13-mongo-/frontend
npm run dev

# Check backend logs
# Look at the terminal where backend is running
```

---

**The backend is working perfectly. The issue is likely on the frontend/browser side. Check the browser console for the specific error!**
