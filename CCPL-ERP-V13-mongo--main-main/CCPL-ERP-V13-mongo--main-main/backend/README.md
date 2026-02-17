# Inventory Management ERP - Backend

FastAPI + MongoDB backend for the Inventory Management System.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Create `.env` file:

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=inventory_erp
SECRET_KEY=your-super-secret-key-minimum-32-characters
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Open `http://localhost:8000/docs` (Swagger) or `http://localhost:8000/redoc` (ReDoc)

## Project Structure

- `/app/models` - Pydantic/Beanie database models
- `/app/routes` - API routes
- `/app/core` - Security, authentication, dependencies
- `/app/services` - Business logic
- `/app/utils` - Utility functions
