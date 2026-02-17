#!/bin/bash

echo "================================"
echo "Inventory ERP - Quick Start"
echo "================================"
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✓ Docker found"
    echo ""
    echo "Starting with Docker Compose (Atlas)..."
    echo ""
    
    # Start services
    docker-compose up -d

    echo ""
    echo "Initializing database (creating admin user if not exists)..."
    sleep 3
    docker-compose exec -T backend python init_db.py

    echo ""
    echo "================================"
    echo "Services Started!"
    echo "================================"
    echo ""
    echo "MongoDB:     Atlas (MONGODB_URL from environment)"
    echo "Backend API: http://localhost:8000"
    echo "Frontend:    http://localhost:5173"
    echo ""
    echo "API Docs:    http://localhost:8000/docs"
    echo ""
    echo "Default Login Credentials:"
    echo "  Email:    admin@inventoryerp.com"
    echo "  Password: Admin@123"
    echo ""
    echo "View logs:   docker-compose logs -f"
    echo "Stop:        docker-compose down"
    echo ""
else
    echo "✗ Docker not found. Using manual setup..."
    echo ""
    
    # Backend setup
    echo "Starting MongoDB..."
    echo "Make sure MongoDB is running on localhost:27017"
    echo ""
    
    # Backend
    echo "Setting up Backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python -m venv venv
    fi
    
    # Activate venv
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi
    
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
    
    echo "Starting backend server..."
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    
    cd ../frontend
    
    echo ""
    echo "Setting up Frontend..."
    
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    echo "Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    echo ""
    echo "================================"
    echo "Services Started!"
    echo "================================"
    echo ""
    echo "Backend API: http://localhost:8000"
    echo "Frontend:    http://localhost:5173"
    echo "API Docs:    http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop servers"
    echo ""
    
    wait $BACKEND_PID $FRONTEND_PID
fi
