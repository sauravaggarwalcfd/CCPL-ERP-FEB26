// PM2 config - Linux / Codespaces only
// Windows uses direct pm2 start commands in start.bat
const path = require('path')
const isWin = process.platform === 'win32'

module.exports = {
  apps: [
    {
      name: 'ccpl-backend',
      cwd: path.join(__dirname, 'backend'),
      script: isWin ? path.join(__dirname, 'backend', 'venv_win', 'Scripts', 'python.exe') : 'python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload',
      interpreter: 'none',
      watch: false,
      env: { PORT: 8000 }
    },
    {
      name: 'ccpl-frontend',
      cwd: path.join(__dirname, 'frontend'),
      script: isWin ? 'cmd' : 'npx',
      args: isWin ? '/c npm run dev -- --host 0.0.0.0 --port 8085 --strictPort' : 'vite --host 0.0.0.0 --port 8085 --strictPort',
      interpreter: 'none',
      watch: false,
      env: { PORT: 8085 }
    }
  ]
}
