import { createContext, useState, useEffect, useCallback } from 'react'
import { authService } from '../services/authService'

export const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tokenExpiresAt, setTokenExpiresAt] = useState(null)

  // Check if token is about to expire (within 5 minutes)
  const isTokenExpiringSoon = useCallback(() => {
    if (!tokenExpiresAt) return false
    const now = new Date()
    const timeUntilExpiry = new Date(tokenExpiresAt) - now
    return timeUntilExpiry < 5 * 60 * 1000 // 5 minutes
  }, [tokenExpiresAt])

  // Initialize auth from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const expiresAt = localStorage.getItem('token_expires_at')
        
        if (token && expiresAt) {
          setTokenExpiresAt(expiresAt)
          // Try to fetch user data
          const userData = await authService.getMe()
          setUser(userData)
        }
      } catch (err) {
        console.error('Failed to initialize auth:', err)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('token_expires_at')
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  // Setup token refresh interval
  useEffect(() => {
    let refreshInterval = null

    if (user && tokenExpiresAt) {
      refreshInterval = setInterval(() => {
        if (isTokenExpiringSoon()) {
          refreshToken()
        }
      }, 60000) // Check every minute
    }

    return () => {
      if (refreshInterval) clearInterval(refreshInterval)
    }
  }, [user, tokenExpiresAt, isTokenExpiringSoon])

  const login = async (email, password) => {
    try {
      setError(null)
      const response = await authService.login(email, password)
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      
      // Calculate and store token expiry time
      const expiresAt = new Date(Date.now() + (response.expires_in * 1000))
      localStorage.setItem('token_expires_at', expiresAt.toISOString())
      setTokenExpiresAt(expiresAt.toISOString())
      
      setUser(response.user)
      return response
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed'
      setError(errorMessage)
      throw err
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (err) {
      console.error('Logout API call failed:', err)
      // Continue with local logout even if API fails
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('token_expires_at')
      setUser(null)
      setTokenExpiresAt(null)
      setError(null)
    }
  }

  const refreshToken = async () => {
    try {
      const refreshTokenValue = localStorage.getItem('refresh_token')
      if (!refreshTokenValue) {
        throw new Error('No refresh token available')
      }

      const response = await authService.refresh(refreshTokenValue)
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      
      // Update expiry time
      const expiresAt = new Date(Date.now() + (response.expires_in * 1000))
      localStorage.setItem('token_expires_at', expiresAt.toISOString())
      setTokenExpiresAt(expiresAt.toISOString())
      
      if (response.user) {
        setUser(response.user)
      }
      
      return response
    } catch (err) {
      console.error('Token refresh failed:', err)
      await logout()
      throw err
    }
  }

  const changePassword = async (currentPassword, newPassword, confirmPassword) => {
    try {
      setError(null)
      const response = await authService.changePassword(currentPassword, newPassword, confirmPassword)
      return response
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to change password'
      setError(errorMessage)
      throw err
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      error,
      login,
      logout,
      refreshToken,
      changePassword,
      isTokenExpiringSoon: isTokenExpiringSoon()
    }}>
      {children}
    </AuthContext.Provider>
  )
}

