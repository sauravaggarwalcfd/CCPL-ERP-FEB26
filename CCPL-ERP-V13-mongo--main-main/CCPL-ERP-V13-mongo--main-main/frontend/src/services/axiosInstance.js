import axios from 'axios'
import { API_CONFIG } from '../config/api.config'

// Create axios instance with base configuration
const axiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token to all requests
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(API_CONFIG.ACCESS_TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('❌ Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Handle 401 Unauthorized - Token expired or invalid
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.warn('🔐 Unauthorized - attempting token refresh...')

      // Try to refresh token
      const refreshToken = localStorage.getItem(API_CONFIG.REFRESH_TOKEN_KEY)

      if (refreshToken && !originalRequest.url.includes('/auth/refresh')) {
        originalRequest._retry = true

        try {
          // Attempt token refresh
          const response = await axios.post(
            `${API_CONFIG.BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          )

          const { access_token, refresh_token: newRefreshToken } = response.data

          // Update tokens
          localStorage.setItem(API_CONFIG.ACCESS_TOKEN_KEY, access_token)
          if (newRefreshToken) {
            localStorage.setItem(API_CONFIG.REFRESH_TOKEN_KEY, newRefreshToken)
          }

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          console.log('✅ Token refreshed successfully')
          return axiosInstance(originalRequest)

        } catch (refreshError) {
          console.error('❌ Token refresh failed:', refreshError)
          // Clear all auth data
          localStorage.removeItem(API_CONFIG.ACCESS_TOKEN_KEY)
          localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_KEY)
          localStorage.removeItem(API_CONFIG.USER_KEY)

          // Dispatch custom event for AuthContext to handle
          window.dispatchEvent(new Event('authTokenExpired'))

          // Redirect to login if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token or already on refresh endpoint
        localStorage.removeItem(API_CONFIG.ACCESS_TOKEN_KEY)
        localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_KEY)
        localStorage.removeItem(API_CONFIG.USER_KEY)

        window.dispatchEvent(new Event('authTokenExpired'))

        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }

    // Handle other errors
    const errorMessage = error.response?.data?.detail ||
                        error.response?.data?.message ||
                        error.message ||
                        'An error occurred'

    console.error(`❌ API Error [${error.response?.status || 'Network'}]:`, errorMessage)

    return Promise.reject(error)
  }
)

export default axiosInstance
