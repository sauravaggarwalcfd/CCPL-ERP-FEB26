import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLayout } from '../../context/LayoutContext'
import { Plus, Search, Edit, Trash2, AlertCircle } from 'lucide-react'
import { suppliers } from '../../services/api'
import toast from 'react-hot-toast'

export default function SuppliersList() {
  const { setTitle } = useLayout()
  const navigate = useNavigate()
  const [supplierList, setSupplierList] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const limit = 10

  useEffect(() => {
    setTitle('Suppliers')
    fetchSuppliers()
  }, [setTitle, search, page])

  const fetchSuppliers = async () => {
    try {
      setLoading(true)
      setError('') // Clear previous errors
      const response = await suppliers.list({
        skip: page * limit,
        limit,
        search: search || undefined,
      })
      
      // Handle response format variations
      if (response && response.data) {
        const supplierData = Array.isArray(response.data) 
          ? response.data 
          : (response.data.data || [])
        setSupplierList(supplierData)
      } else {
        setSupplierList([])
      }
    } catch (error) {
      console.error('Error fetching suppliers:', error)
      setSupplierList([])
      
      // More specific error messages for network issues
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        const errorMessage = 'Backend server not available. Please start the server first.'
        setError(errorMessage)
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch suppliers'
        setError(errorMessage)
        toast.error(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this supplier?')) return
    
    try {
      await suppliers.delete(id)
      toast.success('Supplier deleted')
      fetchSuppliers()
    } catch (error) {
      console.error('Error deleting supplier:', error)
      
      // More specific error messages
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        toast.error('Backend server not available. Cannot delete supplier.')
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete supplier'
        toast.error(errorMessage)
      }
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Sticky Top Bar */}
      <div className="bg-white p-4 border-b flex items-center justify-between sticky top-0 z-10 gap-4">
        <div className="flex-1 max-w-md relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search by name, code, or phone..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(0)
            }}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <button
          onClick={() => navigate('/suppliers/new')}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 shadow-sm font-medium transition"
        >
          <Plus size={20} />
          Add Supplier
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading...</div>
          ) : error ? (
            <div className="text-center py-12">
              <AlertCircle size={48} className="mx-auto text-red-400 mb-2" />
              <p className="text-red-600 font-medium mb-2">Error Loading Suppliers</p>
              <p className="text-gray-600 text-sm mb-4">{error}</p>
              <button
                onClick={fetchSuppliers}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
              >
                Try Again
              </button>
            </div>
          ) : supplierList.length === 0 ? (
            <div className="text-center py-12 text-gray-500">No suppliers found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="text-left px-6 py-3 font-medium text-gray-500 uppercase tracking-wider">Code</th>
                    <th className="text-left px-6 py-3 font-medium text-gray-500 uppercase tracking-wider">Company</th>
                    <th className="text-left px-6 py-3 font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                    <th className="text-left px-6 py-3 font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                    <th className="text-left px-6 py-3 font-medium text-gray-500 uppercase tracking-wider">GST</th>
                    <th className="text-left px-6 py-3 font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="text-left px-6 py-3 font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {supplierList.map((supplier) => (
                    <tr key={supplier.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 font-mono text-gray-600">{supplier.code}</td>
                      <td className="px-6 py-4 font-medium text-gray-900">{supplier.company_name}</td>
                      <td className="px-6 py-4 text-gray-600">{supplier.contact_person || '-'}</td>
                      <td className="px-6 py-4 text-gray-600">{supplier.phone}</td>
                      <td className="px-6 py-4 text-gray-600">{supplier.gst_number || '-'}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            supplier.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {supplier.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 flex gap-3">
                        <button
                          onClick={() => navigate(`/suppliers/${supplier.id}`)}
                          className="text-blue-600 hover:text-blue-800 transition"
                          title="Edit"
                        >
                          <Edit size={18} />
                        </button>
                        <button
                          onClick={() => handleDelete(supplier.id)}
                          className="text-red-600 hover:text-red-800 transition"
                          title="Delete"
                        >
                          <Trash2 size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
