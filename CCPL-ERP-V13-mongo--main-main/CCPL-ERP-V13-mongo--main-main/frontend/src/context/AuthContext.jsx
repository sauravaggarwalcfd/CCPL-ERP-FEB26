import { createContext, useState, useEffect, useCallback } from 'react'
import {
  loginUser,
  verifyToken,
  logoutUser,
  getToken,
  getStoredUser,
  changePassword as changePasswordApi
} from '../services/authApi'

export const AuthContext = createContext()

function AuthProvider({ children }) {
  const [loading, setLoading] = useState(true)
  const [isAuth, setIsAuth] = useState(false)
  const [user, setUser] = useState(null)
  const [error, setError] = useState(null)

  // Initialize authentication on mount
  useEffect(() => {
    const initAuth = async () => {
      setLoading(true)
      console.log('🔄 Initializing authentication...')

      try {
        const token = getToken()

        if (!token) {
          console.log('ℹ️ No token found - user not authenticated')
          setIsAuth(false)
          setUser(null)
          setLoading(false)
          return
        }

        console.log('🔍 Verifying token with server...')
        const verifyResult = await verifyToken()

        if (verifyResult && verifyResult.valid) {
          setIsAuth(true)
          setUser(verifyResult.user || getStoredUser())
          console.log('✅ Authentication verified - user logged in')
        } else {
          console.warn('⚠️ Token invalid - clearing auth data')
          setIsAuth(false)
          setUser(null)
        }
      } catch (err) {
        console.error('❌ Auth initialization error:', err)
        // If server verification fails but we have a token, assume authenticated
        // (handles offline scenarios)
        const token = getToken()
        if (token) {
          const storedUser = getStoredUser()
          if (storedUser) {
            setIsAuth(true)
            setUser(storedUser)
            console.warn('⚠️ Using offline auth - could not verify with server')
          } else {
            setIsAuth(false)
            setUser(null)
          }
        } else {
          setIsAuth(false)
          setUser(null)
        }
      } finally {
        setLoading(false)
      }
    }

    initAuth()
  }, [])

  // Listen for token expiration events from axios interceptor
  useEffect(() => {
    const handleTokenExpired = () => {
      console.warn('🔐 Token expired event received')
      setIsAuth(false)
      setUser(null)
      setError('Session expired. Please login again.')
    }

    window.addEventListener('authTokenExpired', handleTokenExpired)
    return () => window.removeEventListener('authTokenExpired', handleTokenExpired)
  }, [])

  /**
   * Login user
   */
  const login = useCallback(async (email, password) => {
    try {
      setError(null)
      console.log('🔐 Logging in user:', email)

      const { token, user: userData } = await loginUser(email, password)

      setIsAuth(true)
      setUser(userData)

      console.log('✅ Login successful')
      return true
    } catch (err) {
      const message = err.message || 'Login failed. Please try again.'
      console.error('❌ Login failed:', message)
      setError(message)
      setIsAuth(false)
      setUser(null)
      return false
    }
  }, [])

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      setError(null)
      console.log('👋 Logging out user...')

      await logoutUser()

      setIsAuth(false)
      setUser(null)

      console.log('✅ Logout successful')
    } catch (err) {
      console.error('❌ Logout error:', err)
      // Still clear local state even if API call fails
      setIsAuth(false)
      setUser(null)
    }
  }, [])

  /**
   * Change password
   */
  const changePassword = useCallback(async (currentPassword, newPassword, confirmPassword) => {
    try {
      setError(null)
      console.log('🔑 Changing password...')

      const response = await changePasswordApi(currentPassword, newPassword, confirmPassword)

      console.log('✅ Password changed successfully')
      return response
    } catch (err) {
      const message = err.message || 'Failed to change password'
      console.error('❌ Password change failed:', message)
      setError(message)
      throw err
    }
  }, [])

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  /**
   * Update user data
   */
  const updateUser = useCallback((userData) => {
    setUser(userData)
  }, [])

  const value = {
    // State
    loading,
    isAuth,
    user,
    error,

    // Actions
    login,
    logout,
    changePassword,
    clearError,
    updateUser,

    // Aliases for backward compatibility
    isAuthenticated: isAuth,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export { AuthProvider }
export default AuthProvider
