import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Search, X, Package, AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { brands } from '../../services/api'

const BRAND_CATEGORIES = ['Textile', 'Trim', 'Button', 'Accessory']

export default function BrandMaster() {
  const [brandList, setBrandList] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [modalMode, setModalMode] = useState('create') // 'create' or 'edit'
  const [selectedBrand, setSelectedBrand] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState(null)

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const itemsPerPage = 20

  // Form data
  const [formData, setFormData] = useState({
    brand_code: '',
    brand_name: '',
    brand_category: 'Textile',
    country: '',
    contact_person: '',
    email: '',
    phone: '',
    website: '',
    is_active: true,
  })

  // Form validation errors
  const [errors, setErrors] = useState({})

  useEffect(() => {
    fetchBrands()
  }, [currentPage, searchTerm])

  const fetchBrands = async () => {
    try {
      setLoading(true)
      const skip = (currentPage - 1) * itemsPerPage
      const params = {
        skip,
        limit: itemsPerPage,
      }

      if (searchTerm) {
        params.search = searchTerm
      }

      const response = await brands.list(params)
      setBrandList(response.data.items || response.data || [])
      setTotalItems(response.data.total || response.data.length || 0)
    } catch (error) {
      toast.error('Failed to fetch brands')
      console.error(error)
      setBrandList([])
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      brand_code: '',
      brand_name: '',
      brand_category: 'Textile',
      country: '',
      contact_person: '',
      email: '',
      phone: '',
      website: '',
      is_active: true,
    })
    setErrors({})
    setSelectedBrand(null)
  }

  const handleCreate = () => {
    resetForm()
    setModalMode('create')
    setShowModal(true)
  }

  const handleEdit = (brand) => {
    setSelectedBrand(brand)
    setModalMode('edit')
    setFormData({
      brand_code: brand.brand_code || '',
      brand_name: brand.brand_name || '',
      brand_category: brand.brand_category || 'Textile',
      country: brand.country || '',
      contact_person: brand.contact_person || '',
      email: brand.email || '',
      phone: brand.phone || '',
      website: brand.website || '',
      is_active: brand.is_active !== undefined ? brand.is_active : true,
    })
    setErrors({})
    setShowModal(true)
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.brand_code.trim()) {
      newErrors.brand_code = 'Brand code is required'
    } else if (!/^[A-Z0-9]{2,10}$/.test(formData.brand_code.toUpperCase())) {
      newErrors.brand_code = 'Brand code must be 2-10 alphanumeric characters'
    }

    if (!formData.brand_name.trim()) {
      newErrors.brand_name = 'Brand name is required'
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format'
    }

    if (formData.website && !/^https?:\/\/.+/.test(formData.website)) {
      newErrors.website = 'Website must start with http:// or https://'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validateForm()) {
      toast.error('Please fix validation errors')
      return
    }

    try {
      const submitData = {
        ...formData,
        brand_code: formData.brand_code.toUpperCase(),
      }

      if (modalMode === 'create') {
        await brands.create(submitData)
        toast.success('Brand created successfully')
      } else {
        await brands.update(selectedBrand.brand_code, submitData)
        toast.success('Brand updated successfully')
      }

      setShowModal(false)
      resetForm()
      fetchBrands()
      setCurrentPage(1)
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Operation failed'
      toast.error(errorMessage)
      console.error(error)
    }
  }

  const handleDeleteClick = (brand) => {
    setDeleteTarget(brand)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (!deleteTarget) return

    try {
      await brands.delete(deleteTarget.brand_code)
      toast.success('Brand deleted successfully')
      setShowDeleteModal(false)
      setDeleteTarget(null)
      fetchBrands()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Delete failed')
      console.error(error)
    }
  }

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value)
    setCurrentPage(1)
  }

  const totalPages = Math.ceil(totalItems / itemsPerPage)

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Package size={32} />
              <div>
                <h1 className="text-2xl font-bold">Brand Master</h1>
                <p className="text-sm text-green-100">
                  {totalItems} brands • Manage brand information
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={handleCreate}
            className="bg-white text-green-700 px-4 py-2 rounded-lg flex items-center gap-2 font-medium hover:bg-green-50 transition"
          >
            <Plus size={20} /> New Brand
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="p-4 border-b bg-white">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search brands by code or name..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto bg-white">
        {loading ? (
          <div className="p-8 text-center text-gray-500">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
            <p>Loading brands...</p>
          </div>
        ) : brandList.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Package size={48} className="mx-auto mb-3 text-gray-300" />
            <p className="font-medium">No brands found</p>
            <p className="text-sm mt-1">Create your first brand to get started</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-green-50 sticky top-0">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-green-900">Code</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-green-900">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-green-900">Category</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-green-900">Country</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-green-900">Contact</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-green-900">Email</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-green-900">Phone</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-green-900">Status</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-green-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {brandList.map((brand) => (
                  <tr key={brand.brand_code} className="hover:bg-green-50 transition">
                    <td className="px-4 py-3">
                      <span className="font-mono text-sm font-medium text-gray-900 bg-gray-100 px-2 py-1 rounded">
                        {brand.brand_code}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{brand.brand_name}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                        {brand.brand_category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{brand.country || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{brand.contact_person || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{brand.email || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{brand.phone || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        brand.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {brand.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleEdit(brand)}
                          className="p-1.5 hover:bg-blue-100 rounded text-blue-600 transition"
                          title="Edit"
                        >
                          <Edit size={16} />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(brand)}
                          className="p-1.5 hover:bg-red-100 rounded text-red-600 transition"
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="p-4 border-t bg-white flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} brands
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={20} />
            </button>
            <div className="flex gap-1">
              {[...Array(totalPages)].map((_, i) => {
                const page = i + 1
                if (
                  page === 1 ||
                  page === totalPages ||
                  (page >= currentPage - 1 && page <= currentPage + 1)
                ) {
                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`px-3 py-1 rounded-lg ${
                        currentPage === page
                          ? 'bg-green-600 text-white'
                          : 'border hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  )
                } else if (page === currentPage - 2 || page === currentPage + 2) {
                  return <span key={page} className="px-2">...</span>
                }
                return null
              })}
            </div>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h3 className="text-lg font-bold text-gray-900">
                {modalMode === 'create' ? 'Create New Brand' : 'Edit Brand'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600 transition"
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                {/* Brand Code & Name */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Brand Code <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.brand_code}
                      onChange={(e) => setFormData({ ...formData, brand_code: e.target.value.toUpperCase() })}
                      disabled={modalMode === 'edit'}
                      maxLength={10}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 uppercase ${
                        modalMode === 'edit' ? 'bg-gray-100 cursor-not-allowed' : ''
                      } ${errors.brand_code ? 'border-red-500' : 'border-gray-300'}`}
                      placeholder="e.g., NIKE"
                      required
                    />
                    {errors.brand_code && (
                      <p className="text-xs text-red-500 mt-1">{errors.brand_code}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Brand Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.brand_name}
                      onChange={(e) => setFormData({ ...formData, brand_name: e.target.value })}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${
                        errors.brand_name ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="e.g., Nike Inc."
                      required
                    />
                    {errors.brand_name && (
                      <p className="text-xs text-red-500 mt-1">{errors.brand_name}</p>
                    )}
                  </div>
                </div>

                {/* Category & Country */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Brand Category
                    </label>
                    <select
                      value={formData.brand_category}
                      onChange={(e) => setFormData({ ...formData, brand_category: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      {BRAND_CATEGORIES.map(category => (
                        <option key={category} value={category}>{category}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Country
                    </label>
                    <input
                      type="text"
                      value={formData.country}
                      onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="e.g., USA"
                    />
                  </div>
                </div>

                {/* Contact Person & Email */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Contact Person
                    </label>
                    <input
                      type="text"
                      value={formData.contact_person}
                      onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="e.g., John Doe"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${
                        errors.email ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="e.g., contact@brand.com"
                    />
                    {errors.email && (
                      <p className="text-xs text-red-500 mt-1">{errors.email}</p>
                    )}
                  </div>
                </div>

                {/* Phone & Website */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone
                    </label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="e.g., +1-234-567-8900"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Website
                    </label>
                    <input
                      type="url"
                      value={formData.website}
                      onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${
                        errors.website ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="e.g., https://www.brand.com"
                    />
                    {errors.website && (
                      <p className="text-xs text-red-500 mt-1">{errors.website}</p>
                    )}
                  </div>
                </div>

                {/* Active Status */}
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                  />
                  <label htmlFor="is_active" className="text-sm font-medium text-gray-700 cursor-pointer">
                    Active Brand
                  </label>
                </div>
              </div>

              {/* Form Actions */}
              <div className="flex gap-3 mt-6 pt-6 border-t">
                <button
                  type="submit"
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition"
                >
                  {modalMode === 'create' ? 'Create Brand' : 'Update Brand'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && deleteTarget && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="text-red-500" size={24} />
              <h3 className="text-lg font-bold text-gray-900">Confirm Deletion</h3>
            </div>

            <p className="text-sm text-gray-600 mb-6">
              Are you sure you want to delete the brand <span className="font-semibold">"{deleteTarget.brand_name}"</span>?
              This action cannot be undone.
            </p>

            <div className="flex gap-3">
              <button
                onClick={confirmDelete}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition"
              >
                Delete
              </button>
              <button
                onClick={() => {
                  setShowDeleteModal(false)
                  setDeleteTarget(null)
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
