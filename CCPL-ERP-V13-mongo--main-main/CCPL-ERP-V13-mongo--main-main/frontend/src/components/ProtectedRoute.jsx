import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 * Shows loading state while checking authentication
 */
// AUTH DISABLED - bypass login for now
export default function ProtectedRoute({ children }) {
  return children
}
