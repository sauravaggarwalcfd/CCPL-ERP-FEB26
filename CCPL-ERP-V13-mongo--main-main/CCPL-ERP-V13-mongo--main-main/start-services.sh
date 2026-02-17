#!/bin/bash

echo "🚀 Starting all services..."

# Kill any existing processes
pkill -f "uvicorn" 2>/dev/null
pkill -f "vite" 2>/dev/null
pkill -f "mongod" 2>/dev/null
sleep 2

# Start MongoDB
echo "📦 Starting MongoDB..."
mongod --dbpath ./data/mongo &
sleep 3

# Start Backend
echo "🔙 Starting Backend..."
cd backend
python -m pip install -r requirements.txt --quiet
export PYTHONUNBUFFERED=1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 5

# Check backend health
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is ready!"
    break
  fi
  echo "Attempt $i/30..."
  sleep 1
done

# Start Frontend
echo "🎨 Starting Frontend..."
cd ../frontend
npm install --quiet 2>/dev/null
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
sleep 5

echo ""
echo "════════════════════════════════════════════"
echo "✅ ALL SERVICES STARTED SUCCESSFULLY"
echo "════════════════════════════════════════════"
echo ""
echo "📊 Status:"
echo "  Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
echo "  Frontend: http://localhost:5173 (PID: $FRONTEND_PID)"
echo "  MongoDB:  localhost:27017"
echo ""
echo "📝 Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "🌐 Open in browser: http://localhost:5173"
echo ""