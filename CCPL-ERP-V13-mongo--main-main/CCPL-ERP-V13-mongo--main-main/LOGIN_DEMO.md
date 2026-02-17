# Login Demo Credentials & Troubleshooting

## ✅ Demo User Created Successfully

### Demo Account Credentials:
```
Email:    demo@example.com
Password: Demo123!
```

## 🚀 Server Status

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:5173 | ✅ Running |
| **Backend API** | http://localhost:8000 | ✅ Running |
| **MongoDB** | mongodb://localhost:27017 | ✅ Running |
| **API Docs** | http://localhost:8000/docs | ✅ Available |

## 📝 How to Login

1. **Open the application** at http://localhost:5173
2. **Click the Login tab** (if on Signup)
3. **Enter credentials:**
   - Email: `demo@example.com`
   - Password: `Demo123!`
4. **Click "Sign In"**
5. **You'll be redirected to the Dashboard**

## 🔍 Login System Overview

### Password Requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*)

### Security Features:
- ✅ Password hashing with bcrypt (12 rounds)
- ✅ JWT token-based authentication
- ✅ Refresh token support
- ✅ Account lockout after 5 failed login attempts
- ✅ 15-minute lockout period
- ✅ Password change enforcement
- ✅ Session management

## 📊 User Status in Database

```
Email: demo@example.com
Status: ACTIVE
Role: User (can be updated)
Created: 2025-12-13
```

## 🔐 API Authentication

The backend API uses **Bearer Token Authentication**:

```bash
# Example API request
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/auth/me
```

### Token Response Format:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "...",
    "email": "demo@example.com",
    "full_name": "Demo User",
    "status": "active"
  }
}
```

## 🐛 Common Login Issues & Fixes

### Issue 1: "Invalid email or password"
- ✅ **Solution**: Check exact spelling of demo@example.com
- ✅ Verify password is exactly: `Demo123!`
- ✅ Password is case-sensitive

### Issue 2: "Account is temporarily locked"
- ✅ **Cause**: 5 failed login attempts
- ✅ **Solution**: Wait 15 minutes for automatic unlock
- ✅ Or delete user from MongoDB and recreate

### Issue 3: "Account is inactive"
- ✅ **Cause**: User status is not ACTIVE
- ✅ **Solution**: Check user status in MongoDB
- ✅ Run: `py create_demo_user.py` to recreate

### Issue 4: CORS errors in browser console
- ✅ **Solution**: Backend must be running on port 8000
- ✅ Check: http://localhost:8000/docs is accessible
- ✅ Verify MongoDB is running

## 🔧 Database Management

### View all users in MongoDB:
```bash
mongosh "mongodb://localhost:27017"
> use inventory_erp
> db.user.find().pretty()
```

### Recreate demo user:
```bash
cd backend
py create_demo_user.py
```

### Reset user lockout (if needed):
```bash
mongosh "mongodb://localhost:27017"
> use inventory_erp
> db.user.updateOne(
    { email: "demo@example.com" },
    { $set: { "security.lock_until": null, "security.failed_login_attempts": 0 } }
  )
```

## 📚 Additional Endpoints

### For Testing API:
- **Login**: `POST /api/auth/login`
- **Signup**: `POST /api/auth/signup`
- **Refresh Token**: `POST /api/auth/refresh`
- **Logout**: `POST /api/auth/logout`
- **Get Current User**: `GET /api/auth/me`
- **Change Password**: `POST /api/auth/change-password`

### API Documentation:
Visit: http://localhost:8000/docs (Swagger UI)

## ✅ Verification Checklist

- [x] MongoDB running on port 27017
- [x] Backend API running on port 8000
- [x] Frontend running on port 5173
- [x] Demo user created in database
- [x] Login endpoint functional
- [x] CORS enabled for frontend
- [x] JWT tokens working

---

**Last Updated**: December 13, 2025
**Status**: ✅ All systems operational
