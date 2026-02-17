# Quick Start Commands

## PowerShell - Start All Services

### Start Backend
```powershell
cd "C:\Users\ABC\Downloads\files\inventory-erp\backend"
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log
```

Or use this one-liner:
```powershell
$python = "C:\Users\ABC\Downloads\files\inventory-erp\backend\venv\Scripts\python.exe"; cd "C:\Users\ABC\Downloads\files\inventory-erp\backend"; & $python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log
```

### Start Frontend
```powershell
cd "C:\Users\ABC\Downloads\files\inventory-erp\frontend"
npm run dev
```

### View in Browser
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Prerequisites

- MongoDB must be running on localhost:27017
  ```powershell
  # Check if MongoDB is running
  Test-NetConnection -ComputerName localhost -Port 27017
  ```

- Python virtual environment already created
- npm dependencies already installed

## Verify Services

### Check Backend
```powershell
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Check Frontend  
```powershell
curl http://localhost:5173
# Should return HTML page
```

### Check MongoDB
```powershell
Test-NetConnection -ComputerName localhost -Port 27017
# Should show: TcpTestSucceeded : True
```

## Kill Running Processes

If you need to stop everything:
```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Kill all Node processes
taskkill /F /IM node.exe
```

## Troubleshooting

### Port already in use
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object -Property OwningProcess
# Kill the process
Stop-Process -Id <PID> -Force
```

### MongoDB not found
- Start MongoDB from Services or command line
- Default connection: mongodb://localhost:27017

### npm module not found
```powershell
cd "C:\Users\ABC\Downloads\files\inventory-erp\frontend"
npm install --legacy-peer-deps
```

## API Testing

### Signup
```powershell
$body = @{
    full_name = "Test User"
    email = "test@example.com"
    password = "TestPass123!"
    confirm_password = "TestPass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/signup" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### Login
```powershell
$body = @{
    email = "test@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

## Project Structure

```
inventory-erp/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── auth.py (signup, login endpoints)
│   │   ├── core/
│   │   │   ├── security.py (password hashing, tokens)
│   │   │   └── dependencies.py (auth validation)
│   │   └── main.py (FastAPI app)
│   ├── venv/ (Python virtual environment)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── authService.js (API calls)
│   │   ├── context/
│   │   │   └── AuthContext.jsx (state management)
│   │   └── pages/
│   │       └── Login.jsx (signup/login UI)
│   └── package.json
│
├── .env (environment variables)
├── SYSTEM_READY.md (this file with testing guide)
└── AUTHENTICATION_GUIDE.md (detailed docs)
```

## Database

- **Type**: MongoDB (document database)
- **Connection**: mongodb://localhost:27017
- **Database**: inventory_erp
- **Collections**: users, roles, products, etc.

Default collections created on first run with user signup/login.

## Security Notes

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Enable password requirements in config
- Use MongoDB Atlas for cloud database
- Set proper CORS origins
- Enable HTTPS-only cookies

See AUTHENTICATION_GUIDE.md for production setup.
