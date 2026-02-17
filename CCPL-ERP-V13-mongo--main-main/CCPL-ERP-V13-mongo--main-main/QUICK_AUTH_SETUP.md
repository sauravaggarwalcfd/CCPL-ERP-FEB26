# Authentication Quick Reference

## 🔐 What's New

Your authentication system has been enhanced with **enterprise-grade security** that prevents failures and attacks.

## 🚀 Key Features

### Token Management
- **Access Token**: 15 minutes (short-lived, for API calls)
- **Refresh Token**: 7 days (longer-lived, for getting new access tokens)
- **Auto Refresh**: Frontend automatically refreshes tokens 5 minutes before expiry
- **Token Blacklist**: Logout invalidates tokens immediately

### Password Security
```
Must contain:
✓ 8+ characters
✓ At least 1 uppercase letter (A-Z)
✓ At least 1 number (0-9)
✓ At least 1 special character (!@#$%^&*)

Example: MyPassword123!
```

### Login Protection
- **5 strikes rule**: Account locks after 5 failed attempts
- **30-minute lockout**: Account unlocks automatically after 30 minutes
- **Audit logging**: All attempts logged for security review

## 📝 New Endpoints

### Change Password
```bash
POST /api/auth/change-password

Body:
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!",
  "confirm_password": "NewPass456!"
}
```

## 🛠️ Configuration

Edit `backend/app/config.py` to customize:

```python
# Token timing
ACCESS_TOKEN_EXPIRE_MINUTES = 15      # How long access token lasts
REFRESH_TOKEN_EXPIRE_DAYS = 7         # How long refresh token lasts

# Password rules
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL = True

# Login security
MAX_LOGIN_ATTEMPTS = 5                 # Failed attempts before lockout
LOGIN_LOCKOUT_MINUTES = 30             # How long to lock account
PASSWORD_HASH_ROUNDS = 12              # Higher = slower but more secure
```

## 🔧 Testing

### Login Test
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Password123!"}'

# Returns:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 900,
  "user": { ... }
}
```

### API Call Test
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Change Password Test
```bash
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123!",
    "new_password": "NewPass456!",
    "confirm_password": "NewPass456!"
  }'
```

## ⚙️ Common Issues & Fixes

### "Invalid token" Error
**Why**: Token expired or malformed
**Fix**: Log in again to get new token

### "Account is locked" Error
**Why**: Too many failed login attempts
**Fix**: Wait 30 minutes or ask admin to unlock

### "Password must contain uppercase letter" Error
**Why**: Password doesn't meet requirements
**Fix**: Add uppercase letter to password (Example: MyPassword123!)

### "Invalid or expired refresh token" Error
**Why**: Refresh token expired or blacklisted
**Fix**: Log in again to get new tokens

## 📊 Security Improvements

| Before | After | Impact |
|--------|-------|--------|
| 24-hour tokens | 15-min tokens | 96% less exposure |
| Manual refresh | Auto refresh | Zero downtime |
| Unlimited attempts | 5-attempt lockout | Blocks brute force |
| Any password | Strong passwords | Better security |
| Token reuse after logout | Token blacklist | True logout |

## 🚀 Production Deployment

Before deploying to production:

1. **Generate a strong SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update config.py**
   ```python
   ENVIRONMENT = "production"
   SECRET_KEY = "YOUR_GENERATED_KEY_HERE"  # From step 1
   DEBUG = False
   ```

3. **Enable HTTPS**
   ```python
   SECURE_COOKIES = True
   ```

4. **Set allowed origins**
   ```python
   ALLOWED_ORIGINS = ["https://yourdomain.com"]
   ```

5. **Use environment variables** (.env file)
   ```
   ENVIRONMENT=production
   SECRET_KEY=your_super_secret_key_here
   MONGODB_URL=mongodb://your_server
   ```

## 📚 Learn More

- Read `AUTHENTICATION_GUIDE.md` for detailed documentation
- Read `AUTHENTICATION_CHANGES.md` for all changes made
- Check logs for authentication events: `backend/logs/`

## 🆘 Quick Troubleshooting

**Q: Token keeps expiring?**
A: Tokens expire after 15 minutes. Frontend auto-refreshes. Log in again if issue persists.

**Q: Account locked?**
A: Wait 30 minutes or ask admin to unlock. Don't retry immediately (triggers more failures).

**Q: Change password not working?**
A: Ensure new password meets complexity rules (8+ chars, uppercase, number, special char).

**Q: Getting CORS errors?**
A: Add frontend URL to `ALLOWED_ORIGINS` in `backend/app/config.py`

**Q: Login response different?**
A: Response now includes `expires_in` field with token lifetime in seconds.

## 🔐 Security Reminders

✓ Never share tokens in logs or with others
✓ Always use HTTPS in production
✓ Never commit SECRET_KEY to git
✓ Use environment variables for secrets
✓ Rotate SECRET_KEY periodically
✓ Monitor login failures
✓ Keep libraries updated

## 📞 Support

For detailed help:
1. Check `AUTHENTICATION_GUIDE.md` (comprehensive guide)
2. Review `AUTHENTICATION_CHANGES.md` (what changed)
3. Check `backend/logs/` for error details
4. Review API responses for specific error messages
