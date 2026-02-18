// Auto-detect Codespaces or use environment variable
const getApiUrl = () => {
  // Check if we're in Codespaces
  if (window.location.hostname.includes('app.github.dev')) {
    const codespaceUrl = window.location.origin.replace('-8085', '-8000')
    return `${codespaceUrl}/api`
  }

  // Use environment variable or default to localhost
  return import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
}

export const API_CONFIG = {
  BASE_URL: getApiUrl(),
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  ACCESS_TOKEN_KEY: import.meta.env.VITE_ACCESS_TOKEN_KEY || 'access_token',
  REFRESH_TOKEN_KEY: import.meta.env.VITE_REFRESH_TOKEN_KEY || 'refresh_token',
  USER_KEY: import.meta.env.VITE_USER_KEY || 'current_user',
}

console.log('🔧 API Configuration:', {
  baseUrl: API_CONFIG.BASE_URL,
  environment: window.location.hostname.includes('app.github.dev') ? 'Codespaces' : 'Local'
})
