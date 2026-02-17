import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Search, X, Truck, AlertTriangle, ChevronLeft, ChevronRight, Filter } from 'lucide-react'
import toast from 'react-hot-toast'
import { suppliers } from '../../services/api'

const SUPPLIER_TYPES = ['Textile Supplier', 'Cotton Supplier', 'Trim Supplier']
const PAYMENT_TERMS = ['Net 30', 'Net 60', 'Advance', 'COD']

export default function SupplierMaster() {
  const [supplierList, setSupplierList] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCity, setFilterCity] = useState('')
  const [filterType, setFilterType] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [modalMode, setModalMode] = useState('create') // 'create' or 'edit'
  const [selectedSupplier, setSelectedSupplier] = useState(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState(null)

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const itemsPerPage = 20

  // Form data
  const [formData, setFormData] = useState({
    supplier_code: '',
    supplier_name: '',
    supplier_type: 'Textile Supplier',
    country: '',
    city: '',
    contact_person: '',
    email: '',
    phone: '',
    website: '',
    address: '',
    gst_number: '',
    bank_account: '',
    payment_terms: 'Net 30',
    is_active: true,
  })

  // Form validation errors
  const [errors, setErrors] = useState({})

  // Get unique cities for filter dropdown
  const [cities, setCities] = useState([])

  useEffect(() => {
    fetchSuppliers()
  }, [currentPage, searchTerm, filterCity, filterType])

  useEffect(() => {
    // Extract unique cities from supplier list
    const uniqueCities = [...new Set(supplierList.map(s => s.city).filter(Boolean))]
    setCities(uniqueCities.sort())
  }, [supplierList])

  const fetchSuppliers = async () => {
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

      if (filterCity) {
        params.city = filterCity
      }

      if (filterType) {
        params.supplier_type = filterType
      }

      const response = await suppliers.list(params)
      setSupplierList(response.data.items || response.data || [])
      setTotalItems(response.data.total || response.data.length || 0)
    } catch (error) {
      toast.error('Failed to fetch suppliers')
      console.error(error)
      setSupplierList([])
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      supplier_code: '',
      supplier_name: '',
      supplier_type: 'Textile Supplier',
      country: '',
      city: '',
      contact_person: '',
      email: '',
      phone: '',
      website: '',
      address: '',
      gst_number: '',
      bank_account: '',
      payment_terms: 'Net 30',
      is_active: true,
    })
    setErrors({})
    setSelectedSupplier(null)
  }

  const handleCreate = () => {
    resetForm()
    setModalMode('create')
    setShowModal(true)
  }

  const handleEdit = (supplier) => {
    setSelectedSupplier(supplier)
    setModalMode('edit')
    setFormData({
      supplier_code: supplier.supplier_code || '',
      supplier_name: supplier.supplier_name || '',
      supplier_type: supplier.supplier_type || 'Textile Supplier',
      country: supplier.country || '',
      city: supplier.city || '',
      contact_person: supplier.contact_person || '',
      email: supplier.email || '',
      phone: supplier.phone || '',
      website: supplier.website || '',
      address: supplier.address || '',
      gst_number: supplier.gst_number || '',
      bank_account: supplier.bank_account || '',
      payment_terms: supplier.payment_terms || 'Net 30',
      is_active: supplier.is_active !== undefined ? supplier.is_active : true,
    })
    setErrors({})
    setShowModal(true)
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.supplier_code.trim()) {
      newErrors.supplier_code = 'Supplier code is required'
    } else if (!/^[A-Z0-9]{2,10}$/.test(formData.supplier_code.toUpperCase())) {
      newErrors.supplier_code = 'Supplier code must be 2-10 alphanumeric characters'
    }

    if (!formData.supplier_name.trim()) {
      newErrors.supplier_name = 'Supplier name is required'
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format'
    }

    if (formData.website && !/^https?:\/\/.+/.test(formData.website)) {
      newErrors.website = 'Website must start with http:// or https://'
    }

    if (formData.gst_number && !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(formData.gst_number)) {
      newErrors.gst_number = 'Invalid GST number format'
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
        supplier_code: formData.supplier_code.toUpperCase(),
        gst_number: formData.gst_number.toUpperCase(),
      }

      if (modalMode === 'create') {
        await suppliers.create(submitData)
        toast.success('Supplier created successfully')
      } else {
        await suppliers.update(selectedSupplier.supplier_code, submitData)
        toast.success('Supplier updated successfully')
      }

      setShowModal(false)
      resetForm()
      fetchSuppliers()
      setCurrentPage(1)
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Operation failed'
      toast.error(errorMessage)
      console.error(error)
    }
  }

  const handleDeleteClick = (supplier) => {
    setDeleteTarget(supplier)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (!deleteTarget) return

    try {
      await suppliers.delete(deleteTarget.supplier_code)
      toast.success('Supplier deleted successfully')
      setShowDeleteModal(false)
      setDeleteTarget(null)
      fetchSuppliers()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Delete failed')
      console.error(error)
    }
  }

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value)
    setCurrentPage(1)
  }

  const handleFilterChange = (type, value) => {
    if (type === 'city') {
      setFilterCity(value)
    } else if (type === 'type') {
      setFilterType(value)
    }
    setCurrentPage(1)
  }

  const clearFilters = () => {
    setFilterCity('')
    setFilterType('')
    setSearchTerm('')
    setCurrentPage(1)
  }

  const activeFiltersCount = [filterCity, filterType].filter(Boolean).length

  const totalPages = Math.ceil(totalItems / itemsPerPage)

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Truck size={32} />
              <div>
                <h1 className="text-2xl font-bold">Supplier Master</h1>
                <p className="text-sm text-blue-100">
                  {totalItems} suppliers • Manage supplier information
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={handleCreate}
            className="bg-white text-blue-700 px-4 py-2 rounded-lg flex items-center gap-2 font-medium hover:bg-blue-50 transition"
          >
            <Plus size={20} /> New Supplier
          </button>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="p-4 border-b bg-white space-y-3">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search suppliers by code or name..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2 rounded-lg border flex items-center gap-2 font-medium transition ${
              activeFiltersCount > 0
                ? 'bg-blue-100 border-blue-300 text-blue-700'
                : 'hover:bg-gray-50 border-gray-300'
            }`}
          >
            <Filter size={20} />
            Filters
            {activeFiltersCount > 0 && (
              <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-0.5">
                {activeFiltersCount}
              </span>
            )}
          </button>
        </div>

        {/* Filter Dropdowns */}
        {showFilters && (
          <div className="flex gap-3 p-4 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
              <select
                value={filterCity}
                onChange={(e) => handleFilterChange('city', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Cities</option>
                {cities.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Supplier Type</label>
              <select
                value={filterType}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                {SUPPLIER_TYPES.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 font-medium"
              >
                Clear All
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto bg-white">
        {loading ? (
          <div className="p-8 text-center text-gray-500">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Loading suppliers...</p>
          </div>
        ) : supplierList.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Truck size={48} className="mx-auto mb-3 text-gray-300" />
            <p className="font-medium">No suppliers found</p>
            <p className="text-sm mt-1">
              {searchTerm || filterCity || filterType
                ? 'Try adjusting your search or filters'
                : 'Create your first supplier to get started'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-blue-50 sticky top-0">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">Code</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">Type</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">City</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">Contact</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">Email</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">Phone</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">Payment</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-blue-900">Status</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-blue-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {supplierList.map((supplier) => (
                  <tr key={supplier.supplier_code} className="hover:bg-blue-50 transition">
                    <td className="px-4 py-3">
                      <span className="font-mono text-sm font-medium text-gray-900 bg-gray-100 px-2 py-1 rounded">
                        {supplier.supplier_code}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{supplier.supplier_name}</div>
                        {supplier.gst_number && (
                          <div className="text-xs text-gray-500">GST: {supplier.gst_number}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                        {supplier.supplier_type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-600">
                        {supplier.city && <div>{supplier.city}</div>}
                        {supplier.country && <div className="text-xs text-gray-500">{supplier.country}</div>}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{supplier.contact_person || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{supplier.email || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{supplier.phone || '-'}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                        {supplier.payment_terms}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        supplier.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {supplier.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleEdit(supplier)}
                          className="p-1.5 hover:bg-blue-100 rounded text-blue-600 transition"
                          title="Edit"
                        >
                          <Edit size={16} />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(supplier)}
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
            Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} suppliers
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
                          ? 'bg-blue-600 text-white'
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
          <div className="bg-white rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h3 className="text-lg font-bold text-gray-900">
                {modalMode === 'create' ? 'Create New Supplier' : 'Edit Supplier'}
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
                {/* Supplier Code & Name */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Supplier Code <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.supplier_code}
                      onChange={(e) => setFormData({ ...formData, supplier_code: e.target.value.toUpperCase() })}
                      disabled={modalMode === 'edit'}
                      maxLength={10}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase ${
                        modalMode === 'edit' ? 'bg-gray-100 cursor-not-allowed' : ''
                      } ${errors.supplier_code ? 'border-red-500' : 'border-gray-300'}`}
                      placeholder="e.g., SUPP001"
                      required
                    />
                    {errors.supplier_code && (
                      <p className="text-xs text-red-500 mt-1">{errors.supplier_code}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Supplier Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.supplier_name}
                      onChange={(e) => setFormData({ ...formData, supplier_name: e.target.value })}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.supplier_name ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="e.g., ABC Textiles Ltd."
                      required
                    />
                    {errors.supplier_name && (
                      <p className="text-xs text-red-500 mt-1">{errors.supplier_name}</p>
                    )}
                  </div>
                </div>

                {/* Supplier Type */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Supplier Type
                    </label>
                    <select
                      value={formData.supplier_type}
                      onChange={(e) => setFormData({ ...formData, supplier_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {SUPPLIER_TYPES.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Payment Terms
                    </label>
                    <select
                      value={formData.payment_terms}
                      onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {PAYMENT_TERMS.map(term => (
                        <option key={term} value={term}>{term}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Country & City */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Country
                    </label>
                    <input
                      type="text"
                      value={formData.country}
                      onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., India"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      City
                    </label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Mumbai"
                    />
                  </div>
                </div>

                {/* Address */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address
                  </label>
                  <textarea
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter full address"
                  />
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.email ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="e.g., contact@supplier.com"
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., +91-1234567890"
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
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.website ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="e.g., https://www.supplier.com"
                    />
                    {errors.website && (
                      <p className="text-xs text-red-500 mt-1">{errors.website}</p>
                    )}
                  </div>
                </div>

                {/* GST Number & Bank Account */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      GST Number
                    </label>
                    <input
                      type="text"
                      value={formData.gst_number}
                      onChange={(e) => setFormData({ ...formData, gst_number: e.target.value.toUpperCase() })}
                      maxLength={15}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase ${
                        errors.gst_number ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="e.g., 22AAAAA0000A1Z5"
                    />
                    {errors.gst_number && (
                      <p className="text-xs text-red-500 mt-1">{errors.gst_number}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Bank Account
                    </label>
                    <input
                      type="text"
                      value={formData.bank_account}
                      onChange={(e) => setFormData({ ...formData, bank_account: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., 1234567890"
                    />
                  </div>
                </div>

                {/* Active Status */}
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="is_active" className="text-sm font-medium text-gray-700 cursor-pointer">
                    Active Supplier
                  </label>
                </div>
              </div>

              {/* Form Actions */}
              <div className="flex gap-3 mt-6 pt-6 border-t">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition"
                >
                  {modalMode === 'create' ? 'Create Supplier' : 'Update Supplier'}
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
              Are you sure you want to delete the supplier <span className="font-semibold">"{deleteTarget.supplier_name}"</span>?
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
