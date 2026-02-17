# 🎯 Quick Testing Guide

## Right Now - What You Can Do

### ✅ Current Status
```
🟢 Backend:  http://localhost:8000 ✓
🟢 Frontend: http://localhost:5173 ✓  
🟢 MongoDB:  localhost:27017 ✓
```

### Test 1: Visit the Frontend
**URL**: http://localhost:5173
**Expected**: Inventory ERP login page loads

### Test 2: Create New Account
1. Click "Create a new account"
2. Fill in:
   ```
   Full Name: Test User
   Email: test@example.com
   Password: TestPass123!
   Confirm: TestPass123!
   ```
3. Click "Create Account"
4. **Expected**: Auto-login and redirect to dashboard

### Test 3: Logout and Login
1. Click logout (if there's a logout option)
2. Click "Sign in"
3. Enter:
   ```
   Email: test@example.com
   Password: TestPass123!
   ```
4. Click "Sign in"
5. **Expected**: Login successful, redirect to dashboard

### Test 4: Test Password Requirements
Try these passwords to see validation:
- ❌ `pass` - Too short
- ❌ `password` - No uppercase/number/special
- ❌ `Password1` - No special character
- ✅ `Password123!` - Valid

### Test 5: Test Account Lockout
1. Try logging in with wrong password 5 times
2. On 5th attempt: "Account is temporarily locked"
3. **Expected**: Can't login for 30 minutes

### Test 6: API Testing (Browser Console)
Open browser F12 Developer Tools, Console tab:

```javascript
// Test signup
fetch('http://localhost:8000/api/auth/signup', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    full_name: 'Test',
    email: 'test2@example.com',
    password: 'TestPass123!',
    confirm_password: 'TestPass123!'
  })
}).then(r => r.json()).then(console.log)
```

---

## 🔑 Sample Test Credentials

After first signup, use:
```
Email: test@example.com
Password: TestPass123!
```

Or create your own:
- Name: anything
- Email: anything@example.com
- Password: Must be like: TestPass123! (8+ chars, uppercase, number, special)

---

## 📋 Password Rules

Must have ALL of:
- ✓ 8+ characters
- ✓ At least 1 UPPERCASE letter (A-Z)
- ✓ At least 1 number (0-9)
- ✓ At least 1 special character (!@#$%^&*...)

Examples that WORK:
- ✅ Password123!
- ✅ MySecure456@
- ✅ Test1Pass#Now

Examples that FAIL:
- ❌ password123! (no uppercase)
- ❌ PASSWORD123! (no lowercase)
- ❌ Password! (no number)
- ❌ Password123 (no special char)
- ❌ Pass1! (too short)

---

## 🛠️ If Something Breaks

### Backend Not Running
```powershell
# Check if running
curl http://localhost:8000/health

# If not, restart
cd "C:\Users\ABC\Downloads\files\inventory-erp\backend"
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Not Running
```powershell
# Check if running
curl http://localhost:5173

# If not, restart
cd "C:\Users\ABC\Downloads\files\inventory-erp\frontend"
npm run dev
```

### MongoDB Not Running
```powershell
# Check if running
Test-NetConnection -ComputerName localhost -Port 27017

# If fails, start MongoDB
# Use MongoDB GUI or Services
```

---

## 🎥 Expected Behavior

### Successful Signup
```
User enters:
- Full Name
- Email (must be new)
- Password (must follow rules)

System:
1. Validates email doesn't exist
2. Validates password strength
3. Creates user in MongoDB
4. Returns tokens
5. Auto-logs in user
6. Shows dashboard

URL changes to: http://localhost:5173/dashboard
```

### Successful Login
```
User enters:
- Email
- Password

System:
1. Finds user by email
2. Compares password
3. Returns tokens
4. Logs user in
5. Shows dashboard
```

### Account Lockout (after 5 failed attempts)
```
User enters wrong password 5 times

System:
1. Counts attempts (1, 2, 3, 4, 5)
2. After 5: Locks account
3. Shows: "Account locked for 30 minutes"
4. Requires waiting 30 minutes or password reset
```

---

## 📊 API Endpoints (for advanced testing)

All endpoints at: `http://localhost:8000/api/auth/`

```
POST /signup
  Body: {full_name, email, password, confirm_password}
  Response: {access_token, refresh_token, user}

POST /login
  Body: {email, password}
  Response: {access_token, refresh_token, user}

POST /refresh
  Body: {refresh_token}
  Response: {access_token, refresh_token, user}

GET /me
  Header: Authorization: Bearer {token}
  Response: {user data}

POST /logout
  Header: Authorization: Bearer {token}
  Response: {message}

POST /change-password
  Header: Authorization: Bearer {token}
  Body: {current_password, new_password, confirm_password}
  Response: {message}
```

**View all docs**: http://localhost:8000/docs

---

## ✅ Checklist

After following this guide, check:

- [ ] Can access http://localhost:5173
- [ ] Can create new account
- [ ] Can login with new account
- [ ] Can see dashboard after login
- [ ] Password validation works
- [ ] Account lockout after 5 attempts
- [ ] Can logout
- [ ] Backend logs show activity
- [ ] No error in browser console (F12)

---

## 🎉 Success!

If all items above ✅, then:
- ✅ Authentication system working
- ✅ Database connected
- ✅ Security features active
- ✅ API endpoints functioning
- ✅ Frontend/Backend integrated

**System is ready!** 🚀

---

## 📞 Need Help?

1. **Check logs**: Backend console for errors
2. **Check browser console**: F12 → Console tab
3. **Read docs**: FINAL_SUMMARY.md for details
4. **Restart services**: Kill and restart servers
5. **Check MongoDB**: Is it running?

See **QUICK_START.md** for detailed commands.
