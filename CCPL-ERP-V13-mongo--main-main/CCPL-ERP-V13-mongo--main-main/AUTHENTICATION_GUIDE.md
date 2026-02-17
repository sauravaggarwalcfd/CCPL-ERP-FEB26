# Enhanced Authentication Guide

## Overview

The authentication system has been upgraded with industry best practices to ensure maximum security and reliability. The system uses JWT (JSON Web Tokens) with a two-token approach (access + refresh tokens) combined with multiple security layers.

## Security Features Implemented

### 1. **JWT Token Management**
- **Short-lived Access Tokens**: 15 minutes (configurable)
- **Longer-lived Refresh Tokens**: 7 days (configurable)
- **JWT ID (jti) Claims**: Unique token identifiers for tracking and revocation
- **Token Blacklisting**: Logged-out tokens are invalidated
- **Token Rotation**: Refresh tokens are rotated on use

### 2. **Password Security**
- **Strong Password Hashing**: bcrypt with 12 rounds (configurable)
- **Password Strength Validation**:
  - Minimum 8 characters (configurable)
  - Requires at least one uppercase letter
  - Requires at least one number
  - Requires at least one special character (!@#$%^&*...)
- **Password Change Endpoint**: Secure password update with validation
- **Password History**: Prevents reusing current password

### 3. **Login Security**
- **Failed Login Attempt Tracking**: Monitors failed attempts
- **Account Lockout**: Locks account after 5 failed attempts (configurable)
- **Lockout Duration**: 30 minutes (configurable)
- **Brute Force Protection**: Prevents password guessing attacks
- **Login Logging**: All login attempts are logged

### 4. **Token Validation**
- **Token Type Checking**: Ensures access tokens are used for API calls, refresh tokens for refreshing
- **Token Expiration**: Automatic token expiration based on configured duration
- **Payload Validation**: Ensures all required claims are present
- **User Status Validation**: Confirms user is active before granting access

### 5. **HTTP Security Headers**
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Protects against clickjacking
- **X-XSS-Protection**: Enables XSS protection
- **CORS Configuration**: Restricts allowed origins

### 6. **Frontend Token Management**
- **Automatic Token Refresh**: Refreshes tokens when about to expire (< 5 minutes)
- **Token Expiry Tracking**: Monitors token expiration times
- **Secure Storage**: Tokens stored in localStorage (HttpOnly option available for production)
- **Request Interceptors**: Automatically adds Bearer token to all API requests
- **Response Interceptors**: Handles 401 errors with automatic refresh attempts

## Configuration

Edit `backend/app/config.py` to customize security settings:

```python
# Password requirements
PASSWORD_MIN_LENGTH: int = 8
PASSWORD_REQUIRE_UPPERCASE: bool = True
PASSWORD_REQUIRE_NUMBERS: bool = True
PASSWORD_REQUIRE_SPECIAL: bool = True

# Login security
MAX_LOGIN_ATTEMPTS: int = 5
LOGIN_LOCKOUT_MINUTES: int = 30
PASSWORD_HASH_ROUNDS: int = 12

# Token timing
ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
REFRESH_TOKEN_EXPIRE_DAYS: int = 7

# Token security
TOKEN_BLACKLIST_ENABLED: bool = True
```

## API Endpoints

### POST /api/auth/login
Authenticates user with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": { "id": "1", "name": "Admin" },
    "effective_permissions": ["read", "write"],
    "assigned_warehouses": []
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `423 Locked`: Account locked due to too many failed attempts
- `403 Forbidden`: Account is inactive/suspended

### POST /api/auth/refresh
Refreshes access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:** Same as login response with new tokens

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token

### POST /api/auth/logout
Logs out user and invalidates tokens.

**Request:** Bearer token required in Authorization header

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

### GET /api/auth/me
Gets current authenticated user information.

**Request:** Bearer token required in Authorization header

**Response:** User object (same as login response user field)

### POST /api/auth/change-password
Changes user password.

**Request:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!",
  "confirm_password": "NewPass456!"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Current password is incorrect
- `400 Bad Request`: New password doesn't meet requirements or passwords don't match

## Frontend Usage

### Login Example

```javascript
import { useContext } from 'react'
import { AuthContext } from '../context/AuthContext'

export function LoginPage() {
  const { login, error } = useContext(AuthContext)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = async () => {
    try {
      await login(email, password)
      // Redirect to dashboard
    } catch (err) {
      // Error is set in context
    }
  }

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleLogin() }}>
      <input 
        type="email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)}
      />
      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <div className="error">{error}</div>}
      <button type="submit">Login</button>
    </form>
  )
}
```

### Protected Routes Example

```javascript
import { useContext } from 'react'
import { AuthContext } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'

export function ProtectedRoute({ children }) {
  const { user, loading } = useContext(AuthContext)

  if (loading) return <div>Loading...</div>
  if (!user) return <Navigate to="/login" />
  
  return children
}
```

### Change Password Example

```javascript
import { useContext, useState } from 'react'
import { AuthContext } from '../context/AuthContext'

export function ChangePasswordForm() {
  const { changePassword, error } = useContext(AuthContext)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [success, setSuccess] = useState('')

  const handleChangePassword = async () => {
    try {
      await changePassword(currentPassword, newPassword, confirmPassword)
      setSuccess('Password changed successfully!')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      // Error is set in context
    }
  }

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleChangePassword() }}>
      <input 
        type="password" 
        placeholder="Current Password"
        value={currentPassword}
        onChange={(e) => setCurrentPassword(e.target.value)}
      />
      <input 
        type="password" 
        placeholder="New Password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
      />
      <input 
        type="password" 
        placeholder="Confirm Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
      />
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
      <button type="submit">Change Password</button>
    </form>
  )
}
```

## Production Deployment Checklist

- [ ] Set `ENVIRONMENT` to "production" in `config.py`
- [ ] Change `SECRET_KEY` to a strong random string (minimum 32 characters)
- [ ] Set `DEBUG` to False
- [ ] Configure `ALLOWED_ORIGINS` with your domain
- [ ] Enable `SECURE_COOKIES` (requires HTTPS)
- [ ] Enable `HTTPONLY_COOKIES`
- [ ] Set `SAMESITE_COOKIES` to "strict"
- [ ] Use environment variables for sensitive settings (.env file)
- [ ] Implement Redis-based token blacklist (instead of in-memory)
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure proper CORS headers
- [ ] Set up audit logging for all authentication events
- [ ] Implement rate limiting on auth endpoints

## Troubleshooting

### "Invalid or expired token" error
- **Cause**: Access token has expired
- **Solution**: The frontend automatically refreshes tokens. If this persists, clear localStorage and login again

### "Account is locked" error
- **Cause**: Too many failed login attempts (default: 5)
- **Solution**: Wait 30 minutes for account to unlock, or admin can unlock manually

### "Password must contain..." error
- **Cause**: Password doesn't meet strength requirements
- **Solution**: Ensure password has uppercase, number, special character, and is 8+ characters

### Token refresh failing
- **Cause**: Refresh token expired or invalid
- **Solution**: User must login again

### CORS errors with auth requests
- **Cause**: Frontend origin not in allowed origins list
- **Solution**: Add frontend URL to `ALLOWED_ORIGINS` in config.py

## Security Best Practices

1. **Always use HTTPS in production**
2. **Never expose SECRET_KEY in code**
3. **Rotate SECRET_KEY periodically**
4. **Monitor failed login attempts for brute force attacks**
5. **Keep token expiration times reasonable**
6. **Use strong, unique SECRET_KEY (32+ characters)**
7. **Enable audit logging for all auth events**
8. **Implement additional 2FA for sensitive accounts**
9. **Regularly update dependencies**
10. **Use environment variables for all secrets**

## Token Flow Diagram

```
┌─────────┐              ┌─────────────┐              ┌──────────┐
│ Client  │              │   Backend   │              │   DB     │
└────┬────┘              └──────┬──────┘              └────┬─────┘
     │                          │                          │
     │  POST /login             │                          │
     ├─────────────────────────>│                          │
     │  (email, password)       │  Query user              │
     │                          ├─────────────────────────>│
     │                          │<─────────────────────────┤
     │                          │  Verify password         │
     │                          │  Create tokens           │
     │<─────────────────────────┤                          │
     │  access_token            │  Update login info       │
     │  refresh_token           ├─────────────────────────>│
     │                          │<─────────────────────────┤
     │                          │                          │
     │  (After 15 min)          │                          │
     │  Token about to expire   │                          │
     │  POST /refresh           │                          │
     ├─────────────────────────>│                          │
     │  (refresh_token)         │  Validate refresh token  │
     │                          │  Create new tokens       │
     │<─────────────────────────┤                          │
     │  new_access_token        │                          │
     │  new_refresh_token       │                          │
     │                          │                          │
     │  POST /logout            │                          │
     ├─────────────────────────>│                          │
     │  (access_token)          │  Blacklist tokens        │
     │<─────────────────────────┤                          │
     │  success                 │                          │
     │                          │                          │
```

## Support

For issues or questions regarding authentication, please:
1. Check the logs in `backend/` for detailed error messages
2. Review the error responses in the API
3. Verify configuration in `config.py`
4. Check browser console for frontend errors
