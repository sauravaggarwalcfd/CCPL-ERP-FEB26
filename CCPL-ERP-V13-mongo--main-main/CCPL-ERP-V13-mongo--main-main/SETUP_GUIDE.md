# CCPL ERP - Complete Setup Guide

## MongoDB Atlas Connection - FIXED ✓

Your application is now configured to work with MongoDB Atlas and automatically initialize on every restart.

## What Was Fixed

### 1. MongoDB Connection String
- **Fixed:** Corrected cluster domain from `cluster0.emapilt.mongodb.net` to `cluster0.empai1t.mongodb.net`
- **Location:** `.env` and `backend/.env`

### 2. Pydantic Validation Error
- **Fixed:** Removed `DB_PASSWORD` environment variable (not needed in Settings model)
- **Files Updated:**
  - `.env`
  - `backend/.env`
  - `docker-compose.yml`

### 3. Admin User Creation
- **Fixed:** Corrected `init_db.py` to use proper model structures
- **Changes:**
  - Fixed import statements (removed non-existent `Address` class)
  - Updated to use `EmbeddedRole` instead of `Role` for user creation
  - Changed address to use dict format instead of class

### 4. Automatic Database Initialization
- **Added:** Database initialization runs automatically on container startup
- **Files Updated:**
  - `docker-compose.yml` - Added init script to startup command
  - `start.sh` - Added database initialization step
  - `README.md` - Updated with correct credentials and setup instructions

## How to Start the Application

### Option 1: Using the Start Script (Recommended)
```bash
./start.sh
```

This will:
1. Start all Docker containers
2. Automatically initialize the database
3. Create the admin user if it doesn't exist
4. Display login credentials

### Option 2: Using Docker Compose
```bash
docker-compose up -d
```

The database initialization runs automatically as part of the backend startup command.

### Option 3: Manual Restart
```bash
docker-compose down
docker-compose up -d
```

## Default Login Credentials

**These credentials work every time you start the application:**

```
Email:    admin@inventoryerp.com
Password: Admin@123
```

## Accessing the Application

### In GitHub Codespaces:
- **Frontend:** https://ominous-enigma-jjv4wpjw767w3xvp-5173.app.github.dev
- **Backend API:** Change port 5173 to 8000 in the URL
- **API Docs:** Same backend URL + `/docs`

### Locally:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Configuration Files

### Root `.env` File
```env
MONGODB_URL=mongodb+srv://tech_db_user:Tech3112@cluster0.empai1t.mongodb.net/?appName=Cluster0
DATABASE_NAME=inventory_erp
SECRET_KEY=your-super-secret-key-min-32-characters-change-in-production
```

### `backend/.env` File
```env
MONGODB_URL=mongodb+srv://tech_db_user:Tech3112@cluster0.empai1t.mongodb.net/?appName=Cluster0
DATABASE_NAME=inventory_erp
APP_NAME=Inventory ERP
DEBUG=True
SECRET_KEY=your-super-secret-key-minimum-32-characters-for-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Permanent Solution Summary

The application now includes a **fully automated initialization system** that:

1. ✓ Runs automatically on every container startup
2. ✓ Creates admin user if it doesn't exist
3. ✓ Creates sample data (warehouse, supplier, customer)
4. ✓ Works seamlessly across restarts
5. ✓ No manual intervention required

## Troubleshooting

### If login still fails:
```bash
# Manually run the initialization script
docker-compose exec backend python init_db.py
```

### View backend logs:
```bash
docker-compose logs backend -f
```

### Check if user was created:
```bash
docker-compose exec backend python check_users.py
```

### Restart everything:
```bash
docker-compose down
docker-compose up -d
```

## Database Information

- **Database:** inventory_erp
- **Collections:** 33 collections with data
- **Provider:** MongoDB Atlas (Cloud)
- **Cluster:** cluster0.empai1t.mongodb.net

## Next Steps

1. **Log in** using the default credentials
2. **Change the admin password** from the settings
3. **Create additional users** with appropriate roles
4. **Configure** warehouses, products, and inventory
5. **Update** SECRET_KEY in production

## Support

If you encounter any issues:
1. Check the backend logs: `docker-compose logs backend`
2. Verify MongoDB Atlas connection
3. Ensure IP is whitelisted in MongoDB Atlas
4. Run `docker-compose down && docker-compose up -d` to restart

---

**Last Updated:** 2025-12-24
**Status:** All systems operational ✓
