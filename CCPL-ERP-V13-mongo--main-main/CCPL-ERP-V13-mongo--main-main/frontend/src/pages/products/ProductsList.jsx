import { Construction, ArrowLeft, Clock, ShoppingBag } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function ProductsList() {
  const navigate = useNavigate()

  return (
    <div className="flex-1 overflow-auto min-h-[80vh] flex items-center justify-center bg-gray-50 p-6">
      <div className="max-w-lg w-full text-center">
        {/* Animated Icon */}
        <div className="relative mx-auto w-32 h-32 mb-8">
          <div className="absolute inset-0 bg-purple-100 rounded-full animate-pulse"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <ShoppingBag className="w-16 h-16 text-purple-600 animate-bounce" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Products
        </h1>

        {/* Status Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-800 rounded-full mb-6">
          <Clock className="w-4 h-4" />
          <span className="font-medium">Work in Progress</span>
        </div>

        {/* Description */}
        <p className="text-gray-600 mb-8 leading-relaxed">
          We're building a powerful product management module with advanced features for 
          product catalogs, variants, and pricing. Coming soon!
        </p>

        {/* Features Coming */}
        <div className="bg-white rounded-lg shadow p-6 mb-8 text-left">
          <h3 className="font-semibold text-gray-900 mb-4">Features Coming Soon:</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-center gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              Product catalog management
            </li>
            <li className="flex items-center gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              Multi-variant support (size, color, etc.)
            </li>
            <li className="flex items-center gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              Pricing and discount management
            </li>
            <li className="flex items-center gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              Product images and media gallery
            </li>
          </ul>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-500 mb-2">
            <span>Development Progress</span>
            <span>Coming Soon</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-gradient-to-r from-purple-400 to-purple-600 h-2 rounded-full w-1/4 animate-pulse"></div>
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
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}
