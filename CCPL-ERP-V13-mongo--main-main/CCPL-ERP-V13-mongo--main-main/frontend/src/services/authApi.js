import axios from 'axios'
import axiosInstance from './axiosInstance'
import { API_CONFIG } from '../config/api.config'

/**
 * Login user with email and password
 * Uses JSON format (not form-data) as per your backend API
 */
export const loginUser = async (email, password) => {
  try {
    console.log('🔐 Attempting login for:', email)

    // Use plain axios (not axiosInstance) to avoid interceptor loop
    const response = await axios.post(
      `${API_CONFIG.BASE_URL}/auth/login`,
      { email, password },  // JSON format
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      }
    )

    const { access_token, refresh_token, user } = response.data

    if (!access_token) {
      throw new Error('No access token received from server')
    }

    // Store tokens and user data
    localStorage.setItem(API_CONFIG.ACCESS_TOKEN_KEY, access_token)
    if (refresh_token) {
      localStorage.setItem(API_CONFIG.REFRESH_TOKEN_KEY, refresh_token)
    }
    if (user) {
      localStorage.setItem(API_CONFIG.USER_KEY, JSON.stringify(user))
    }

    console.log('✅ Login successful for:', email)
    return { token: access_token, user, refreshToken: refresh_token }

  } catch (error) {
    const message = error.response?.data?.detail ||
                   error.response?.data?.message ||
                   error.message ||
                   'Login failed'

    console.error('❌ Login error:', message)
    throw new Error(message)
  }
}

/**
 * Verify current authentication token
 */
export const verifyToken = async () => {
  try {
    const token = localStorage.getItem(API_CONFIG.ACCESS_TOKEN_KEY)

    if (!token) {
      return { valid: false, reason: 'No token found' }
    }

    // Try to get current user info to verify token
    const response = await axiosInstance.get('/auth/me')

    return {
      valid: true,
      user: response.data
    }
  } catch (error) {
    console.error('❌ Token verification failed:', error.message)
    return {
      valid: false,
      reason: error.response?.data?.detail || error.message
    }
  }
}

/**
 * Refresh authentication token
 */
export const refreshAuthToken = async () => {
  try {
    const refreshToken = localStorage.getItem(API_CONFIG.REFRESH_TOKEN_KEY)

    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await axios.post(
      `${API_CONFIG.BASE_URL}/auth/refresh`,
      { refresh_token: refreshToken }
    )

    const { access_token, refresh_token: newRefreshToken } = response.data

    localStorage.setItem(API_CONFIG.ACCESS_TOKEN_KEY, access_token)
    if (newRefreshToken) {
      localStorage.setItem(API_CONFIG.REFRESH_TOKEN_KEY, newRefreshToken)
    }

    console.log('✅ Token refreshed successfully')
    return access_token
  } catch (error) {
    console.error('❌ Token refresh failed:', error)
    throw error
  }
}

/**
 * Logout user and clear all auth data
 */
export const logoutUser = async () => {
  try {
    // Try to call logout endpoint
    await axiosInstance.post('/auth/logout')
    console.log('✅ Logout API call successful')
  } catch (error) {
    console.warn('⚠️ Logout API call failed (continuing with local logout):', error.message)
  } finally {
    // Always clear local storage regardless of API call result
    localStorage.removeItem(API_CONFIG.ACCESS_TOKEN_KEY)
    localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_KEY)
    localStorage.removeItem(API_CONFIG.USER_KEY)
    console.log('✅ Logged out locally')
  }
}

/**
 * Get stored access token
 */
export const getToken = () => {
  return localStorage.getItem(API_CONFIG.ACCESS_TOKEN_KEY)
}

/**
 * Get stored refresh token
 */
export const getRefreshToken = () => {
  return localStorage.getItem(API_CONFIG.REFRESH_TOKEN_KEY)
}

/**
 * Get stored user data
 */
export const getStoredUser = () => {
  try {
    const userStr = localStorage.getItem(API_CONFIG.USER_KEY)
    return userStr ? JSON.parse(userStr) : null
  } catch (error) {
    console.error('❌ Error parsing stored user:', error)
    return null
  }
}

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!getToken()
}

/**
 * Change user password
 */
export const changePassword = async (currentPassword, newPassword, confirmPassword) => {
  try {
    const response = await axiosInstance.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })

    console.log('✅ Password changed successfully')
    return response.data
  } catch (error) {
    const message = error.response?.data?.detail || error.message || 'Password change failed'
    console.error('❌ Password change error:', message)
    throw new Error(message)
  }
}
