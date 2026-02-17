import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    // Log error to console or error reporting service
    console.error('ErrorBoundary caught an error:', error)
    console.error('Error info:', errorInfo)

    // You can also log the error to an error reporting service here
    // logErrorToService(error, errorInfo)

    this.setState({
      error,
      errorInfo
    })
  }

  handleReload = () => {
    window.location.reload()
  }

  handleGoBack = () => {
    window.history.back()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
            <div className="flex items-center justify-center mb-6">
              <div className="rounded-full bg-red-100 p-4">
                <AlertTriangle size={48} className="text-red-600" />
              </div>
            </div>

            <h1 className="text-2xl font-bold text-center text-gray-900 mb-2">
              Oops! Something went wrong
            </h1>

            <p className="text-center text-gray-600 mb-6">
              We apologize for the inconvenience. An unexpected error has occurred.
            </p>

            {this.state.error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <h3 className="text-sm font-semibold text-red-800 mb-2">
                  Error Details:
                </h3>
                <p className="text-sm text-red-700 font-mono">
                  {this.state.error.toString()}
                </p>
              </div>
            )}

            {import.meta.env.VITE_ENABLE_DEBUG === 'true' && this.state.errorInfo && (
              <details className="mb-6 p-4 bg-gray-100 border border-gray-300 rounded-lg">
                <summary className="text-sm font-semibold text-gray-800 cursor-pointer mb-2">
                  Stack Trace (Debug Mode)
                </summary>
                <pre className="text-xs text-gray-700 overflow-x-auto whitespace-pre-wrap">
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div className="flex gap-4 justify-center">
              <button
                onClick={this.handleReload}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition font-medium"
              >
                <RefreshCw size={18} />
                Reload Page
              </button>
              <button
                onClick={this.handleGoBack}
                className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg transition font-medium"
              >
                Go Back
              </button>
            </div>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-500">
                If this problem persists, please contact support.
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
