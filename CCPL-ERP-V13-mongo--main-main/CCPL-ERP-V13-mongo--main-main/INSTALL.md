# Inventory ERP - Complete Setup Guide

A full-stack Inventory Management ERP system with FastAPI backend and React frontend.

## Features

### Phase 1-6 Complete Implementation
- ✅ User Authentication & Authorization
- ✅ Product Management
- ✅ Warehouse Management
- ✅ Inventory Tracking & Stock Movements
- ✅ Supplier Management
- ✅ Purchase Orders
- ✅ Customer Management
- ✅ Sales Orders
- ✅ Stock Transfers
- ✅ Comprehensive Reports & Analytics
- ✅ Barcode Support
- ✅ Multi-warehouse Support

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: MongoDB with Motor & Beanie ORM
- **Authentication**: JWT tokens
- **Async**: Python asyncio

### Frontend
- **Framework**: React 18.2.0
- **Routing**: React Router v6
- **State**: Zustand + React Query
- **UI**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP**: Axios

## Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB 5.0+
- Docker & Docker Compose (optional)

## Installation & Setup

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- MongoDB on port 27017
- Backend API on port 8000
- Frontend on port 5173

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Start MongoDB (ensure it's running)
mongod

# Run backend server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000/api" > .env

# Start development server
npm run dev
```

## Environment Configuration

### Backend .env
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=inventory_erp
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880
```

### Frontend .env
```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Inventory ERP
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user

### Suppliers
- `GET /api/suppliers` - List suppliers
- `POST /api/suppliers` - Create supplier
- `GET /api/suppliers/{id}` - Get supplier details
- `PUT /api/suppliers/{id}` - Update supplier
- `DELETE /api/suppliers/{id}` - Delete supplier

### Purchase Orders
- `GET /api/purchase-orders` - List POs
- `POST /api/purchase-orders` - Create PO
- `GET /api/purchase-orders/{id}` - Get PO details
- `POST /api/purchase-orders/{id}/confirm` - Confirm PO
- `POST /api/purchase-orders/{id}/receive` - Receive goods

### Customers
- `GET /api/customers` - List customers
- `POST /api/customers` - Create customer
- `GET /api/customers/{id}` - Get customer details
- `GET /api/customers/{id}/orders` - Get customer orders

### Sale Orders
- `GET /api/sale-orders` - List orders
- `POST /api/sale-orders` - Create order
- `GET /api/sale-orders/{id}` - Get order details
- `POST /api/sale-orders/{id}/confirm` - Confirm order
- `POST /api/sale-orders/{id}/fulfill` - Fulfill order

### Transfers
- `GET /api/transfers` - List transfers
- `POST /api/transfers` - Create transfer
- `GET /api/transfers/{id}` - Get transfer details
- `POST /api/transfers/{id}/approve` - Approve transfer
- `POST /api/transfers/{id}/ship` - Ship transfer
- `POST /api/transfers/{id}/receive` - Receive transfer

### Inventory
- `GET /api/inventory` - List inventory
- `GET /api/inventory/{id}` - Get inventory details

### Reports
- `GET /api/reports/stock/current` - Current stock report
- `GET /api/reports/stock/low` - Low stock report
- `GET /api/reports/stock/movements` - Stock movements
- `GET /api/reports/sales/summary` - Sales summary
- `GET /api/reports/sales/by-product` - Sales by product
- `GET /api/reports/purchases/summary` - Purchase summary

## Frontend Routes

### Public Routes
- `/login` - Login page

### Protected Routes
- `/` - Dashboard
- `/suppliers` - Suppliers list
- `/suppliers/new` - Create supplier
- `/suppliers/:id` - Supplier details
- `/customers` - Customers list
- `/customers/new` - Create customer
- `/customers/:id` - Customer details
- `/purchase-orders` - PO list
- `/purchase-orders/new` - Create PO
- `/purchase-orders/:id` - PO details
- `/sale-orders` - Sales orders list
- `/sale-orders/new` - Create order
- `/sale-orders/:id` - Order details
- `/transfers` - Transfers list
- `/transfers/new` - Create transfer
- `/transfers/:id` - Transfer details
- `/inventory` - Inventory list
- `/products` - Products list
- `/reports` - Reports dashboard

## Default Credentials

Use these for first login:
- **Email**: admin@inventoryerp.com
- **Password**: Admin@123

*Change these immediately in production!*

## Database Models

### Core Models
- `User` - User accounts and authentication
- `Role` - User roles and permissions
- `Product` - Product master data
- `Warehouse` - Warehouse locations
- `Inventory` - Stock levels by warehouse
- `StockMovement` - Stock transaction history

### Business Models
- `Supplier` - Supplier information
- `PurchaseOrder` - Purchase orders
- `Customer` - Customer information
- `SaleOrder` - Sales orders
- `StockTransfer` - Inter-warehouse transfers
- `StockAdjustment` - Inventory adjustments

### Supporting Models
- `Category` - Product categories
- `Brand` - Product brands
- `Color` - Color variants
- `Size` - Size variants
- `AuditLog` - System audit trail

## Development

### Backend Development
```bash
cd backend

# Run tests
pytest

# Format code
black app/

# Lint code
pylint app/
```

### Frontend Development
```bash
cd frontend

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Deployment

### Docker Deployment
```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Vercel/Netlify (Frontend)
1. Push code to GitHub
2. Connect repository to Vercel/Netlify
3. Set environment variables
4. Deploy

### Railway/Render/Heroku (Backend)
1. Push code to GitHub
2. Connect repository to hosting platform
3. Set environment variables
4. Deploy

## Common Issues & Solutions

### MongoDB Connection Issues
- Ensure MongoDB is running: `mongod`
- Check connection string in .env
- Verify port 27017 is open

### CORS Errors
- Check CORS_ORIGINS in backend .env
- Ensure frontend URL is in CORS whitelist
- Restart backend after changes

### Port Already in Use
```bash
# Find and kill process using port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### Missing Dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## Performance Optimization

### Backend
- Database indexing on frequently searched fields
- Query pagination with limit/offset
- Async operations for I/O
- Caching with Redis (optional)

### Frontend
- Code splitting with React Router
- Lazy loading with React.lazy
- Image optimization
- State management optimization

## Security Considerations

1. **Change Default Credentials**: Update admin password immediately
2. **Secret Key**: Use strong, random SECRET_KEY in production
3. **HTTPS**: Enable SSL/TLS in production
4. **CORS**: Restrict CORS origins to your domain
5. **Rate Limiting**: Implement rate limiting on APIs
6. **Input Validation**: All inputs are validated server-side
7. **SQL Injection**: Using Beanie ORM prevents injection attacks
8. **XSS Protection**: React automatically escapes content

## Support & Documentation

For detailed documentation, see:
- `/backend/README.md` - Backend documentation
- `/frontend/README.md` - Frontend documentation
- `SETUP.md` - Detailed setup instructions

## License

MIT License - See LICENSE file for details

## Contributors

Built with ❤️ for inventory management
