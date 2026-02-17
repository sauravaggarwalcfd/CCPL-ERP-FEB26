# Inventory Management ERP - Complete System

A full-stack Inventory Management ERP system built with React 18, FastAPI, MongoDB, Tailwind CSS, and custom JWT authentication.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite |
| Styling | Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | MongoDB |
| ODM | Pydantic + Beanie + Motor |
| Authentication | Custom JWT |

## Project Structure

```
inventory-erp/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── models/   # Pydantic/Beanie models
│   │   ├── routes/   # API routes
│   │   ├── core/     # Security & dependencies
│   │   ├── services/ # Business logic
│   │   ├── main.py
│   │   ├── config.py
│   │   └── database.py
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── frontend/         # React Vite application
│   ├── src/
│   │   ├── pages/    # Page components
│   │   ├── components/
│   │   ├── context/  # Auth context
│   │   ├── hooks/    # Custom hooks
│   │   ├── services/ # API calls
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── README.md
│
└── docker-compose.yml
```

## Quick Start

### Without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**MongoDB:**
```bash
mongod --dbpath /path/to/data
# Or: docker run -p 27017:27017 mongo:latest
```

### Use MongoDB Atlas (Recommended)

1. **Configure MongoDB Connection:**
   - Set the connection string in `.env` (root) or `backend/.env`:
     ```
     MONGODB_URL=mongodb+srv://tech_db_user:Tech3112@cluster0.empai1t.mongodb.net/?appName=Cluster0
     ```
   - If your password contains special characters like `@` or `/`, URL-encode them (e.g., `Tech@3112` → `Tech%403112`)
   - Ensure your IP address is allowed in MongoDB Atlas Network Access (or use `0.0.0.0/0` for testing)

2. **Start with Docker:**
   ```bash
   ./start.sh
   # Or manually:
   docker-compose up -d
   ```

3. **Automatic Setup:**
   - The backend automatically initializes the database on startup
   - Creates admin user, sample warehouse, supplier, and customer if they don't exist
   - No manual database setup required!

This setup uses MongoDB Atlas (cloud) instead of local MongoDB. The database initialization runs automatically every time you start the containers.

## API Documentation

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend

- Login: http://localhost:5173/login
- Dashboard: http://localhost:5173/dashboard

## Default Login Credentials

After starting the application, use these credentials to log in:

```
Email: admin@inventoryerp.com
Password: Admin@123
```

**Note:** These credentials are automatically created when you first start the application. The admin user is created by the `init_db.py` script that runs on container startup.

## Features

✅ JWT Authentication
✅ User Management & RBAC
✅ Product Management with Variants
✅ Warehouse Management
✅ Inventory Tracking
✅ Stock Movements
✅ Purchase Orders
✅ Sale Orders
✅ Stock Transfers
✅ Stock Adjustments
✅ Master Data Management
✅ Audit Logging

## Database Models

All models are defined with Pydantic and Beanie for MongoDB:

- User (Authentication & Authorization)
- Role & Permission (RBAC)
- Product & ProductVariant
- Warehouse & WarehouseLocation
- Inventory
- StockMovement
- Supplier
- PurchaseOrder
- Customer
- SaleOrder
- StockTransfer
- StockAdjustment
- Category, Brand, Season, Color, Size
- Settings
- AuditLog

## Next Steps

1. **Install dependencies:**
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

2. **Setup MongoDB:**
   - Local: `mongod --dbpath /path/to/data`
   - Docker: `docker run -p 27017:27017 mongo:latest`

3. **Configure environment:**
   - Backend: Update `backend/.env`
   - Frontend: Update `frontend/.env`

4. **Run the application:**
   - Backend: `uvicorn app.main:app --reload`
   - Frontend: `npm run dev`

5. **Access the application:**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

## Development Notes

- All models include timestamps (created_at, updated_at)
- Soft deletes via is_active flag
- Embedded documents for denormalized data
- Indexes on frequently queried fields
- Permission-based access control
- Token-based authentication with refresh tokens

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Products
- `GET /api/products` - List products
- `POST /api/products` - Create product
- `GET /api/products/{id}` - Get product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### More endpoints for Inventory, Orders, Transfers, Adjustments, etc.

## License

Proprietary - Confidence Clothing Inventory System
# Auto-push enabled
