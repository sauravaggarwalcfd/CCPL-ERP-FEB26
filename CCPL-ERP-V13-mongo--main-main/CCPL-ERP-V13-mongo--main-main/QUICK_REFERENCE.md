# Inventory ERP - Quick Reference

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```

### Option 2: Manual Setup
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python init_db.py  # Initialize sample data
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### Option 3: Scripts
```bash
# macOS/Linux
chmod +x start.sh
./start.sh

# Windows
start.bat
```

## 📍 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | Web application |
| API | http://localhost:8000/api | REST API |
| API Docs | http://localhost:8000/docs | Interactive docs |
| MongoDB | localhost:27017 | Database |

## 🔐 Default Credentials

**Email:** admin@inventoryerp.com  
**Password:** Admin@123  

⚠️ **Change immediately in production!**

## 📂 Project Structure

```
inventory-erp/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Data models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── core/           # Auth & dependencies
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # UI components
│   │   ├── services/      # API services
│   │   ├── context/       # React context
│   │   ├── hooks/         # Custom hooks
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── start.sh               # Unix/Linux starter
├── start.bat              # Windows starter
└── README.md
```

## 🔧 Common Commands

### Backend
```bash
cd backend

# Start development server
uvicorn app.main:app --reload

# Initialize database
python init_db.py

# Run tests
pytest

# Format code
black app/
```

### Frontend
```bash
cd frontend

# Development
npm run dev

# Production build
npm run build

# Preview build
npm run preview

# Lint
npm run lint
```

### Docker
```bash
# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache
```

## 📊 Key Features

### Modules
- ✅ Authentication & Authorization
- ✅ Product Management
- ✅ Warehouse Management
- ✅ Inventory Tracking
- ✅ Supplier Management
- ✅ Purchase Orders
- ✅ Customer Management
- ✅ Sales Orders
- ✅ Stock Transfers
- ✅ Reports & Analytics

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | User login |
| GET | /api/suppliers | List suppliers |
| POST | /api/suppliers | Create supplier |
| GET | /api/purchase-orders | List POs |
| POST | /api/purchase-orders | Create PO |
| GET | /api/customers | List customers |
| POST | /api/customers | Create customer |
| GET | /api/sale-orders | List orders |
| POST | /api/sale-orders | Create order |
| GET | /api/transfers | List transfers |
| POST | /api/transfers | Create transfer |
| GET | /api/reports/sales/summary | Sales report |
| GET | /api/reports/stock/current | Inventory report |

## 🔍 Environment Variables

### Backend (.env)
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=inventory_erp
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Inventory ERP
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000

# Kill process
# Windows:
taskkill /PID <PID> /F

# macOS/Linux:
kill -9 <PID>
```

### MongoDB Connection Error
```bash
# Ensure MongoDB is running
mongod

# Or with Docker
docker run -d -p 27017:27017 mongo:latest
```

### Frontend Can't Connect to API
1. Check backend is running: `http://localhost:8000/health`
2. Verify VITE_API_URL in .env
3. Check CORS settings in backend
4. Restart frontend dev server

### Dependencies Issues
```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
npm install
npm audit fix
```

## 📱 Frontend Pages

### Main Pages
- `/` - Dashboard
- `/suppliers` - Supplier list
- `/suppliers/new` - Create supplier
- `/customers` - Customer list
- `/customers/new` - Create customer
- `/purchase-orders` - PO list
- `/purchase-orders/new` - Create PO
- `/sale-orders` - Sales list
- `/sale-orders/new` - Create order
- `/transfers` - Transfers list
- `/transfers/new` - Create transfer
- `/products` - Products list
- `/inventory` - Inventory list
- `/reports` - Reports dashboard

## 🧪 Testing

### API Testing
```bash
# Using curl
curl -X GET http://localhost:8000/api/suppliers

# Using Postman
# Import from http://localhost:8000/docs

# Using pytest
pytest backend/tests/
```

## 📦 Dependencies

### Backend
- FastAPI 0.109.0
- MongoDB (Motor 3.3.2, Beanie 1.25.0)
- Pydantic 2.5.3
- Python-Jose 3.3.0
- Passlib 1.7.4

### Frontend
- React 18.2.0
- React Router 6.20.0
- Axios 1.6.2
- Recharts 2.10.3
- Tailwind CSS 3.3.6

## 🚢 Deployment

### Docker Deployment
```bash
docker-compose -f docker-compose.yml up -d
```

### Cloud Platforms
- **Frontend:** Vercel, Netlify, GitHub Pages
- **Backend:** Railway, Render, PythonAnywhere, Heroku
- **Database:** MongoDB Atlas, Cloud MongoDB

## 📖 Documentation

- `INSTALL.md` - Detailed installation guide
- `SETUP.md` - Configuration guide
- `README.md` - Project overview
- `Backend API Docs` - http://localhost:8000/docs

## 💡 Tips

1. **Development Mode:** Use `-reload` for auto-refresh
2. **Database:** MongoDB Atlas for cloud database
3. **API Testing:** Use http://localhost:8000/docs
4. **Hot Reload:** React fast refresh enabled
5. **Security:** Change SECRET_KEY in production
6. **Logging:** Check terminal for error messages
7. **CORS:** Configure for production domains

## 🆘 Support

For issues:
1. Check error messages in console/terminal
2. Review logs: `docker-compose logs -f`
3. Verify dependencies installed
4. Check environment variables
5. Ensure MongoDB is accessible
6. Restart services

---

**Last Updated:** December 2025  
**Version:** 1.0.0
