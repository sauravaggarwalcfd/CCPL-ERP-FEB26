import { useAuth } from '../../hooks/useAuth'
import { useLayout } from '../../context/LayoutContext'

export default function Header() {
  const { user, logout } = useAuth()
  const { title } = useLayout()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">{user?.full_name}</span>
          <button
            onClick={logout}
            className="text-sm text-red-600 hover:text-red-700"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
