module.exports = {
  apps: [
    {
      name: 'ccpl-backend',
      cwd: './backend',
      script: 'python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload',
      interpreter: 'none',
      watch: false,
      env: {
        PORT: 8000
      }
    },
    {
      name: 'ccpl-frontend',
      cwd: './frontend',
      script: 'npx',
      args: 'vite --host 0.0.0.0 --port 8085 --strictPort',
      interpreter: 'none',
      watch: false,
      env: {
        PORT: 8085
      }
    }
  ]
}
