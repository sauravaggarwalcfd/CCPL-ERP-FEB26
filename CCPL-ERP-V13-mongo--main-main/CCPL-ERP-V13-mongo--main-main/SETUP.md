# Inventory Management ERP - Project Setup

This document guides you through setting up and running the complete system.

## System Requirements

- Python 3.11+
- Node.js 18+
- MongoDB 4.4+
- Git

## Installation & Setup

### 1. Clone/Extract Project

```bash
cd inventory-erp
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. MongoDB Setup

**Option A: Local MongoDB**
```bash
mongod --dbpath /path/to/data
```

**Option B: Docker**
```bash
docker run -d \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin \
  --name mongodb \
  mongo:latest
```

## Running the Application

### Terminal 1: Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: **http://localhost:8000**

API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## Environment Configuration

### Backend (.env)

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=inventory_erp
APP_NAME=Inventory ERP
DEBUG=True
SECRET_KEY=your-super-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000/api
```

## Database Initialization

The database models are automatically created when you run the backend for the first time.

To seed initial data, you'll need to create a seed script. Here's a template:

```python
# backend/seed.py
import asyncio
from app.models.user import User, UserStatus, EmbeddedRole
from app.core.security import get_password_hash
from app.database import connect_to_mongo, close_mongo_connection

async def seed():
    await connect_to_mongo()
    
    # Create admin user
    admin_exists = await User.find_one(User.email == "admin@confidence.com")
    if not admin_exists:
        admin = User(
            email="admin@confidence.com",
            password_hash=get_password_hash("Admin@123"),
            full_name="Admin User",
            status=UserStatus.ACTIVE,
            role=EmbeddedRole(
                id="role_admin",
                name="Super Admin",
                slug="super-admin",
                level=100
            ),
            effective_permissions=["*"]
        )
        await admin.insert()
        print("Admin user created")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed())
```

Then run: `python seed.py`

## Login

```
Email: admin@confidence.com
Password: Admin@123
```

## Docker Deployment (Optional)

```bash
docker-compose up
```

This will start:
- MongoDB on port 27017
- Backend API on port 8000
- Frontend on port 5173

## Troubleshooting

### Backend won't connect to MongoDB
- Ensure MongoDB is running: `mongod --version`
- Check `MONGODB_URL` in `.env`
- Try with local path: `mongodb://localhost:27017`

### Frontend API errors
- Check backend is running on port 8000
- Verify `VITE_API_URL` in frontend `.env`
- Check browser console for CORS errors

### Port already in use
- Backend: Change port in uvicorn command
- Frontend: Vite uses next available port automatically
- MongoDB: Change port with `--port` flag

## Next Development Steps

1. **Implement remaining routes** - Add routes for all CRUD operations
2. **Add permissions system** - Implement role-based access control
3. **Build frontend pages** - Create pages for all major features
4. **Add form validation** - Server and client-side validation
5. **Setup tests** - Unit and integration tests
6. **Deploy to production** - Configure for Emergent Platform

## API Example

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@confidence.com","password":"Admin@123"}'

# Get current user
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer {access_token}"
```

## File Structure Reference

```
backend/
├── app/
│   ├── models/        # Database models
│   │   ├── user.py
│   │   ├── product.py
│   │   └── ...
│   ├── routes/        # API endpoints
│   │   ├── auth.py
│   │   ├── products.py
│   │   └── ...
│   ├── core/
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── main.py
│   ├── config.py
│   └── database.py
├── requirements.txt
├── .env
└── README.md

frontend/
├── src/
│   ├── pages/         # Page components
│   ├── components/    # Reusable components
│   ├── context/       # React context
│   ├── hooks/         # Custom hooks
│   ├── services/      # API services
│   ├── App.jsx
│   └── main.jsx
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Support

For issues or questions, refer to:
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- Original blueprint: `inventory-erp-fastapi-react.md`
