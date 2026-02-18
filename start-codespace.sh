#!/bin/bash
# ============================================================
#   CCPL ERP - Codespace Starter
#   Runs Backend (port 8000) + Frontend (port 8085)
#   and makes both ports PUBLIC for preview
# ============================================================

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/CCPL-ERP-V13-mongo--main-main/CCPL-ERP-V13-mongo--main-main/backend"
FRONTEND_DIR="$ROOT_DIR/CCPL-ERP-V13-mongo--main-main/CCPL-ERP-V13-mongo--main-main/frontend"

echo ""
echo "========================================"
echo "   CCPL Inventory ERP - Codespace"
echo "========================================"
echo ""

# ---- Kill any existing processes on our ports ----
echo "[1/5] Clearing ports 8000 and 8085..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 8085/tcp 2>/dev/null || true
sleep 1

# ---- Install backend deps if needed ----
echo "[2/5] Checking backend dependencies..."
pip install -r "$BACKEND_DIR/requirements.txt" -q

# ---- Install frontend deps if needed ----
echo "[3/5] Checking frontend dependencies..."
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "  Installing npm packages..."
  cd "$FRONTEND_DIR" && npm install
fi

# ---- Make Codespace ports public ----
echo "[4/5] Making ports public..."
gh codespace ports visibility 8000:public 2>/dev/null || true
gh codespace ports visibility 8085:public 2>/dev/null || true

# ---- Start Backend ----
echo "[5/5] Starting services..."
cd "$BACKEND_DIR"
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "  Backend started (PID $BACKEND_PID)"

# ---- Start Frontend ----
cd "$FRONTEND_DIR"
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  Frontend started (PID $FRONTEND_PID)"

# ---- Wait for services ----
echo ""
echo "  Waiting for services to come up..."
sleep 6

# ---- Get Codespace URL ----
CODESPACE_NAME="${CODESPACE_NAME:-$(hostname)}"
if [[ "$HOSTNAME" == *".github.dev"* ]] || [[ -n "$CODESPACES" ]]; then
  BACKEND_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
  FRONTEND_URL="https://${CODESPACE_NAME}-8085.app.github.dev"
else
  BACKEND_URL="http://localhost:8000"
  FRONTEND_URL="http://localhost:8085"
fi

echo ""
echo "========================================"
echo "   Services Running!"
echo "========================================"
echo ""
echo "  Frontend:   $FRONTEND_URL"
echo "  Backend API: $BACKEND_URL"
echo "  API Docs:    $BACKEND_URL/docs"
echo ""
echo "  Login: admin@ccpl.com / Admin@123"
echo ""
echo "  Logs:"
echo "    Backend:  tail -f /tmp/backend.log"
echo "    Frontend: tail -f /tmp/frontend.log"
echo ""
echo "  To stop: kill $BACKEND_PID $FRONTEND_PID"
echo "========================================"
echo ""

# Keep alive and stream backend log
tail -f /tmp/backend.log
