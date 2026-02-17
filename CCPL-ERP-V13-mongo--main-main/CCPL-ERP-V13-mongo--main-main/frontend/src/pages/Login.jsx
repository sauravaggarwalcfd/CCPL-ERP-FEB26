import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Login() {
  const [email, setEmail] = useState('admin@ccpl.com') // Pre-fill for testing
  const [password, setPassword] = useState('Admin@123') // Pre-fill for testing
  const [loggingIn, setLoggingIn] = useState(false)
  const navigate = useNavigate()
  const { login, error, clearError, isAuth, loading } = useAuth()

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuth && !loading) {
      console.log('✅ Already authenticated, redirecting to dashboard')
      navigate('/dashboard', { replace: true })
    }
  }, [isAuth, loading, navigate])

  const handleLogin = async (e) => {
    e.preventDefault()
    clearError()

    if (!email || !password) {
      alert('❌ Please enter email and password')
      return
    }

    setLoggingIn(true)
    console.log('🔐 Attempting login...')

    try {
      const success = await login(email, password)

      if (success) {
        console.log('✅ Login successful, redirecting...')
        navigate('/dashboard', { replace: true })
      } else {
        console.error('❌ Login failed')
      }
    } catch (err) {
      console.error('❌ Login error:', err)
    } finally {
      setLoggingIn(false)
    }
  }

  // Show loading state while initializing auth
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '20px'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
        <h2>Loading...</h2>
        <p style={{ color: '#666' }}>Initializing application...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            🏢 CCPL ERP System
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="rounded-md bg-red-50 p-4 border border-red-200">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-red-400">❌</span>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Login Form */}
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          <div className="rounded-md shadow-sm space-y-3">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loggingIn}
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loggingIn}
              />
            </div>
          </div>

          {/* Login Button */}
          <div>
            <button
              type="submit"
              disabled={loggingIn}
              className={`group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white ${
                loggingIn
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
              }`}
            >
              {loggingIn ? (
                <>
                  <span className="mr-2">⏳</span>
                  Logging in...
                </>
              ) : (
                <>
                  <span className="mr-2">🔐</span>
                  Sign in
                </>
              )}
            </button>
          </div>

          {/* Test Credentials Info */}
          <div className="rounded-md bg-blue-50 p-4 border border-blue-200">
            <div className="text-sm text-blue-700">
              <p className="font-semibold mb-2">📋 Test Credentials:</p>
              <p className="font-mono text-xs">
                Email: admin@ccpl.com<br />
                Password: Admin@123
              </p>
            </div>
          </div>
        </form>

        {/* Footer Info */}
        <div className="text-center text-xs text-gray-500">
          <p>🔒 Secure Login with JWT Authentication</p>
          <p className="mt-1">Auto-detects Codespaces or Local environment</p>
        </div>
      </div>
    </div>
  )
}
