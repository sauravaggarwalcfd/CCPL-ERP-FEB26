import { useState, useEffect, useRef } from 'react'
import { X, Search, Image as ImageIcon, Check, Upload as UploadIcon } from 'lucide-react'
import { files as filesApi } from '../services/api'
import toast from 'react-hot-toast'

export default function ImagePicker({ isOpen, onClose, onSelect, selectedImageId, variant = 'modal' }) {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('item_image')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [activeTab, setActiveTab] = useState('select') // 'select' or 'upload'
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef(null)
  const pageSize = 12

  useEffect(() => {
    if (isOpen && activeTab === 'select') {
      fetchImages()
    }
  }, [isOpen, currentPage, selectedCategory, searchTerm, activeTab])

  const fetchImages = async () => {
    try {
      setLoading(true)
      const params = {
        page: currentPage,
        page_size: pageSize,
        category: selectedCategory,
      }

      if (searchTerm) {
        params.search = searchTerm
      }

      const response = await filesApi.list(params)
      setImages(response.data.files || [])
      setTotalPages(response.data.total_pages || 1)
    } catch (error) {
      console.error('Error fetching images:', error)
      toast.error('Failed to load images')
      setImages([])
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (image) => {
    onSelect({
      image_id: image.file_id,
      image_url: image.file_url,
      image_name: image.original_name,
      thumbnail_url: image.thumbnail_url,
    })
    onClose()
  }

  const handleFileSelect = (event) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
        toast.error('Please upload only JPEG or PNG images')
        event.target.value = ''
        return
      }

      // Validate file size (1MB = 1048576 bytes)
      if (file.size > 1048576) {
        toast.error(`File size (${(file.size / 1024 / 1024).toFixed(2)}MB) exceeds 1MB limit`)
        event.target.value = ''
        return
      }

      handleFileUpload(file)
    }
  }

  const handleFileUpload = async (file) => {
    try {
      setUploading(true)
      setUploadProgress(0)

      const formData = new FormData()
      formData.append('file', file)

      const response = await filesApi.upload(formData, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        setUploadProgress(progress)
      })

      toast.success(`File "${file.name}" uploaded successfully!`)

      // Auto-select the uploaded image
      const uploadedFile = response.data
      onSelect({
        image_id: uploadedFile.file_id,
        image_url: uploadedFile.file_url,
        image_name: uploadedFile.original_name,
        thumbnail_url: uploadedFile.thumbnail_url,
      })

      // Switch to select tab and refresh
      setActiveTab('select')
      fetchImages()

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      onClose()
    } catch (error) {
      console.error('Upload error:', error)
      toast.error(error.response?.data?.detail || 'Failed to upload file')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()

    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile) {
      // Validate file type
      if (!droppedFile.type.match(/^image\/(jpeg|jpg|png)$/)) {
        toast.error('Please upload only JPEG or PNG images')
        return
      }

      // Validate file size (1MB = 1048576 bytes)
      if (droppedFile.size > 1048576) {
        toast.error(`File size (${(droppedFile.size / 1024 / 1024).toFixed(2)}MB) exceeds 1MB limit`)
        return
      }

      handleFileUpload(droppedFile)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  if (!isOpen) return null

  // Panel variant: render inline block without overlay
  if (variant === 'panel') {
    return (
      <div className="bg-white rounded-lg w-full max-h-[80vh] overflow-hidden flex flex-col border border-gray-200">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">Select Image</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('select')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'select'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <ImageIcon className="w-4 h-4" />
              <span>Select from Library</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'upload'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <UploadIcon className="w-4 h-4" />
              <span>Upload New</span>
            </div>
          </button>
        </div>

        {/* Upload Tab Content */}
        {activeTab === 'upload' && (
          <div className="flex-1 overflow-y-auto p-6">
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors bg-gray-50"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <UploadIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">
                {uploading ? `Uploading... ${uploadProgress}%` : 'Drag and drop an image here, or click to select'}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Supported formats: JPEG, PNG only (Max 1MB)
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload-picker"
                disabled={uploading}
              />
              <label
                htmlFor="file-upload-picker"
                className={`inline-block px-6 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors ${
                  uploading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {uploading ? 'Uploading...' : 'Select File'}
              </label>

              {uploading && (
                <div className="mt-4 max-w-md mx-auto">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Select Tab Content */}
        {activeTab === 'select' && (
          <>
            {/* Filters */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex gap-4">
                {/* Search */}
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Search images..."
                      value={searchTerm}
                      onChange={(e) => {
                        setSearchTerm(e.target.value)
                        setCurrentPage(1)
                      }}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Category Filter */}
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value)
                    setCurrentPage(1)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Categories</option>
                  <option value="item_image">Item Images</option>
                  <option value="product_image">Product Images</option>
                  <option value="logo">Logos</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            {/* Image Grid */}
            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-gray-600">Loading images...</p>
                </div>
              ) : images.length === 0 ? (
                <div className="text-center py-12">
                  <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No images found</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Try adjusting your search or category filter
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {images.map((image) => (
                    <div
                      key={image.id}
                      onClick={() => handleSelect(image)}
                      className={`
                        relative border-2 rounded-lg overflow-hidden cursor-pointer transition-all hover:shadow-lg
                        ${selectedImageId === image.file_id ? 'border-blue-500 ring-2 ring-blue-500' : 'border-gray-200 hover:border-blue-300'}
                      `}
                    >
                      {/* Image */}
                      <div className="aspect-square bg-gray-100">
                        <img
                          src={filesApi.getThumbnailUrl(image.thumbnail_url) || filesApi.getFileUrl(image.file_url)}
                          alt={image.original_name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f3f4f6" width="200" height="200"/%3E%3Ctext fill="%239ca3af" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Image%3C/text%3E%3C/svg%3E'
                          }}
                        />
                      </div>

                      {/* Selected Indicator */}
                      {selectedImageId === image.file_id && (
                        <div className="absolute top-2 right-2 bg-blue-500 text-white rounded-full p-1">
                          <Check className="w-4 h-4" />
                        </div>
                      )}

                      {/* Image Name */}
                      <div className="p-2 bg-white">
                        <p className="text-xs text-gray-700 truncate" title={image.original_name}>
                          {image.original_name}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && !loading && (
              <div className="p-4 border-t border-gray-200 flex items-center justify-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-gray-700">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    )
  }

  // Default modal variant with blur background
  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-blue-800 text-white">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Image Manager</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Tabs in Header */}
          <div className="flex gap-3">
            <button
              onClick={() => setActiveTab('select')}
              className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'select'
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <ImageIcon className="w-5 h-5" />
                <span>Select Image</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'upload'
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <UploadIcon className="w-5 h-5" />
                <span>Upload New</span>
              </div>
            </button>
          </div>
        </div>

        {/* Upload Tab Content */}
        {activeTab === 'upload' && (
          <div className="flex-1 overflow-y-auto p-8">
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors bg-gray-50"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <UploadIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2 text-lg">
                {uploading ? `Uploading... ${uploadProgress}%` : 'Drag and drop an image here, or click to select'}
              </p>
              <p className="text-sm text-gray-500 mb-6">
                Supported formats: JPEG, PNG only (Max 1MB)
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload-modal"
                disabled={uploading}
              />
              <label
                htmlFor="file-upload-modal"
                className={`inline-block px-8 py-3 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors text-lg font-medium ${
                  uploading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {uploading ? 'Uploading...' : 'Select File'}
              </label>

              {uploading && (
                <div className="mt-6 max-w-md mx-auto">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Select Tab Content */}
        {activeTab === 'select' && (
          <>
            {/* Filters */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex gap-4">
                {/* Search */}
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Search images..."
                      value={searchTerm}
                      onChange={(e) => {
                        setSearchTerm(e.target.value)
                        setCurrentPage(1)
                      }}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Category Filter */}
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value)
                    setCurrentPage(1)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Categories</option>
                  <option value="item_image">Item Images</option>
                  <option value="product_image">Product Images</option>
                  <option value="logo">Logos</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            {/* Image Grid */}
            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-gray-600">Loading images...</p>
                </div>
              ) : images.length === 0 ? (
                <div className="text-center py-12">
                  <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No images found</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Try adjusting your search or category filter
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                  {images.map((image) => (
                    <div
                      key={image.id}
                      onClick={() => handleSelect(image)}
                      className={`
                        relative border-2 rounded-lg overflow-hidden cursor-pointer transition-all hover:shadow-lg
                        ${selectedImageId === image.file_id ? 'border-blue-500 ring-2 ring-blue-500' : 'border-gray-200 hover:border-blue-300'}
                      `}
                    >
                      {/* Image */}
                      <div className="aspect-square bg-gray-100">
                        <img
                          src={filesApi.getThumbnailUrl(image.thumbnail_url) || filesApi.getFileUrl(image.file_url)}
                          alt={image.original_name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f3f4f6" width="200" height="200"/%3E%3Ctext fill="%239ca3af" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Image%3C/text%3E%3C/svg%3E'
                          }}
                        />
                      </div>

                      {/* Selected Indicator */}
                      {selectedImageId === image.file_id && (
                        <div className="absolute top-2 right-2 bg-blue-500 text-white rounded-full p-1">
                          <Check className="w-4 h-4" />
                        </div>
                      )}

                      {/* Image Name */}
                      <div className="p-2 bg-white">
                        <p className="text-xs text-gray-700 truncate" title={image.original_name}>
                          {image.original_name}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && !loading && (
              <div className="p-4 border-t border-gray-200 flex items-center justify-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-gray-700">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
