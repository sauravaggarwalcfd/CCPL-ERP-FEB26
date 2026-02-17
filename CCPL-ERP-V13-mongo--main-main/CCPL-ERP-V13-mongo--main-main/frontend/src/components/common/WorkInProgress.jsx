import { Construction, ArrowLeft, Clock } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'

export default function WorkInProgress({ title, description }) {
  const navigate = useNavigate()
  const location = useLocation()
  
  // Extract page title from path if not provided
  const pageTitle = title || location.pathname
    .split('/')
    .pop()
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 p-6">
      <div className="max-w-lg w-full text-center">
        {/* Animated Construction Icon */}
        <div className="relative mx-auto w-32 h-32 mb-8">
          <div className="absolute inset-0 bg-yellow-100 rounded-full animate-pulse"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <Construction className="w-16 h-16 text-yellow-600 animate-bounce" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {pageTitle}
        </h1>

        {/* Status Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-800 rounded-full mb-6">
          <Clock className="w-4 h-4" />
          <span className="font-medium">Work in Progress</span>
        </div>

        {/* Description */}
        <p className="text-gray-600 mb-8 leading-relaxed">
          {description || "We're actively working on this feature. It will be available soon. Thank you for your patience!"}
        </p>

        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-500 mb-2">
            <span>Development Progress</span>
            <span>Coming Soon</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 h-2 rounded-full w-1/4 animate-pulse"></div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition font-medium"
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </button>
          <button
            onClick={() => navigate('/')}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
          >
            Go to Dashboard
          </button>
        </div>

        {/* Footer Note */}
        <p className="mt-8 text-sm text-gray-400">
          Need this feature urgently? Contact the development team.
        </p>
      </div>
    </div>
  )
}
