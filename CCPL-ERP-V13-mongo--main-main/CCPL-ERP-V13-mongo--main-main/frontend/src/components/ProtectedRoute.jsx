import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 * Shows loading state while checking authentication
 */
export default function ProtectedRoute({ children }) {
  const { loading, isAuth } = useAuth()

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '20px',
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '48px',
          marginBottom: '20px'
        }}>
          ⏳
        </div>
        <h2>Loading...</h2>
        <p style={{ color: '#666' }}>Initializing application...</p>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuth) {
    console.warn('🔐 Access denied - redirecting to login')
    return <Navigate to="/login" replace />
  }

  // Render protected content
  return children
}
