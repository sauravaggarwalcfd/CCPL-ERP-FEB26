#!/bin/bash
# CCPL ERP - PM2 Startup Script (Linux / Codespaces)

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

echo ""
echo "  ============================================"
echo "    CCPL Inventory ERP (PM2)"
echo "  ============================================"
echo ""

# ===== Check PM2 =====
if ! command -v pm2 &>/dev/null; then
    echo "  Installing PM2..."
    npm install -g pm2
fi

# ===== Install Python deps if needed =====
echo "[1/3] Checking Python dependencies..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "  Installing Python packages..."
    pip install -r "$BACKEND_DIR/requirements.txt"
}

# ===== Install Node deps if needed =====
echo "[2/3] Checking Node dependencies..."
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "  Installing npm packages..."
    cd "$FRONTEND_DIR" && npm install
fi

# ===== Stop any existing PM2 processes =====
pm2 delete ccpl-backend ccpl-frontend 2>/dev/null

# ===== Start with PM2 =====
echo ""
echo "[3/3] Starting servers with PM2..."
cd "$ROOT"
pm2 start ecosystem.config.cjs

echo ""
echo "  Backend  : http://localhost:8000"
echo "  Frontend : http://localhost:8085"
echo ""
echo "  PM2 Commands:"
echo "    pm2 status        - Check server status"
echo "    pm2 logs          - View live logs"
echo "    pm2 logs ccpl-backend   - Backend logs only"
echo "    pm2 logs ccpl-frontend  - Frontend logs only"
echo "    pm2 restart all   - Restart both servers"
echo "    pm2 stop all      - Stop both servers"
echo ""
