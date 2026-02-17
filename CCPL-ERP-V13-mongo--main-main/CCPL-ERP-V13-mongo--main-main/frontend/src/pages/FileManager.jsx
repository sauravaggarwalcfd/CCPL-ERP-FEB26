import { useState, useEffect, useRef } from 'react'
import { Upload, Search, Filter, Trash2, Eye, X, Image, FileText, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { files as filesApi } from '../services/api'

export default function FileManager() {
  const [filesList, setFilesList] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [selectedFile, setSelectedFile] = useState(null)
  const [showPreview, setShowPreview] = useState(false)

  const fileInputRef = useRef(null)

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalFiles, setTotalFiles] = useState(0)
  const pageSize = 20

  useEffect(() => {
    fetchFiles()
  }, [currentPage, selectedCategory, searchTerm])

  const fetchFiles = async () => {
    try {
      setLoading(true)
      const params = {
        page: currentPage,
        page_size: pageSize,
      }

      if (selectedCategory) {
        params.category = selectedCategory
      }

      if (searchTerm) {
        params.search = searchTerm
      }

      const response = await filesApi.list(params)
      setFilesList(response.data.files || [])
      setTotalFiles(response.data.total || 0)
      setTotalPages(response.data.total_pages || 1)
    } catch (error) {
      console.error('Error fetching files:', error)
      toast.error(error.response?.data?.detail || 'Failed to load files')
      setFilesList([])
    } finally {
      setLoading(false)
    }
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

      // Set category if selected
      const category = selectedCategory || 'item_image'
      const response = await filesApi.upload(formData, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        setUploadProgress(progress)
      })

      toast.success(`File "${file.name}" uploaded successfully!`)
      fetchFiles() // Refresh the list

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
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

  const handleDelete = async (fileId, fileName) => {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) {
      return
    }

    try {
      await filesApi.delete(fileId, false) // soft delete
      toast.success('File deleted successfully')
      fetchFiles()
    } catch (error) {
      console.error('Delete error:', error)
      toast.error(error.response?.data?.detail || 'Failed to delete file')
    }
  }

  const handleView = (file) => {
    setSelectedFile(file)
    setShowPreview(true)
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">File Manager</h1>
        <p className="text-gray-600 mt-1">Upload and manage your images and files</p>
      </div>

      {/* Upload Area */}
      <div
        className="mb-6 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors bg-gray-50"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
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
          id="file-upload"
          disabled={uploading}
        />
        <label
          htmlFor="file-upload"
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

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-4">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search files..."
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
          <option value="banner">Banners</option>
          <option value="document">Documents</option>
          <option value="other">Other</option>
        </select>
      </div>

      {/* Stats */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {filesList.length} of {totalFiles} files
      </div>

      {/* Files Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading files...</p>
        </div>
      ) : filesList.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Image className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No files found</p>
          <p className="text-sm text-gray-500 mt-1">Upload your first file to get started</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filesList.map((file) => (
              <div
                key={file.id}
                className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow bg-white"
              >
                {/* Image Preview */}
                <div className="aspect-square bg-gray-100 relative group">
                  {file.thumbnail_url || file.file_url ? (
                    <img
                      src={filesApi.getThumbnailUrl(file.thumbnail_url) || filesApi.getFileUrl(file.file_url)}
                      alt={file.original_name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f3f4f6" width="200" height="200"/%3E%3Ctext fill="%239ca3af" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Image%3C/text%3E%3C/svg%3E'
                      }}
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <FileText className="w-12 h-12 text-gray-400" />
                    </div>
                  )}

                  {/* Hover Actions */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                    <button
                      onClick={() => handleView(file)}
                      className="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
                      title="View"
                    >
                      <Eye className="w-4 h-4 text-gray-700" />
                    </button>
                    <button
                      onClick={() => handleDelete(file.file_id, file.original_name)}
                      className="p-2 bg-white rounded-full hover:bg-red-100 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </div>

                {/* File Info */}
                <div className="p-3">
                  <p className="text-sm font-medium text-gray-800 truncate" title={file.original_name}>
                    {file.original_name}
                  </p>
                  <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                    <span>{file.file_size_formatted || formatFileSize(file.file_size)}</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                      {file.category}
                    </span>
                  </div>
                  {file.width && file.height && (
                    <p className="text-xs text-gray-500 mt-1">
                      {file.width} × {file.height}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
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

      {/* Preview Modal */}
      {showPreview && selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-800">File Preview</h2>
              <button
                onClick={() => setShowPreview(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6">
              {/* Image */}
              <div className="mb-6 flex justify-center bg-gray-50 rounded-lg p-4">
                <img
                  src={filesApi.getFileUrl(selectedFile.file_url)}
                  alt={selectedFile.original_name}
                  className="max-w-full max-h-[500px] object-contain"
                  onError={(e) => {
                    e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3Ctext fill="%239ca3af" font-family="sans-serif" font-size="16" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EImage not available%3C/text%3E%3C/svg%3E'
                  }}
                />
              </div>

              {/* File Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">File ID:</span>
                  <p className="text-gray-600">{selectedFile.file_id}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">File Name:</span>
                  <p className="text-gray-600">{selectedFile.original_name}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Size:</span>
                  <p className="text-gray-600">{selectedFile.file_size_formatted || formatFileSize(selectedFile.file_size)}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Type:</span>
                  <p className="text-gray-600">{selectedFile.file_type}</p>
                </div>
                {selectedFile.width && selectedFile.height && (
                  <div>
                    <span className="font-medium text-gray-700">Dimensions:</span>
                    <p className="text-gray-600">{selectedFile.width} × {selectedFile.height}</p>
                  </div>
                )}
                <div>
                  <span className="font-medium text-gray-700">Category:</span>
                  <p className="text-gray-600">{selectedFile.category}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Upload Date:</span>
                  <p className="text-gray-600">{formatDate(selectedFile.upload_date)}</p>
                </div>
                {selectedFile.uploaded_by_name && (
                  <div>
                    <span className="font-medium text-gray-700">Uploaded By:</span>
                    <p className="text-gray-600">{selectedFile.uploaded_by_name}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
              <button
                onClick={() => setShowPreview(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
