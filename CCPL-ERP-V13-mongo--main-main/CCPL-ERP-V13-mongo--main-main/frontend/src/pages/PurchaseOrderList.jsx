import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus, Search, Filter, Download, Eye, Edit2, Trash2,
  FileText, CheckCircle, XCircle, Clock, Package
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useLayout } from '../context/LayoutContext'
import { purchaseOrders } from '../services/api'

const PurchaseOrderList = () => {
  const { setTitle } = useLayout()
  const navigate = useNavigate()

  // State
  const [poList, setPOList] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterSupplier, setFilterSupplier] = useState('')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0
  })

  // Fetch POs
  const fetchPOs = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {
        skip: pagination.skip,
        limit: pagination.limit
      }

      if (filterStatus) params.status = filterStatus
      if (filterSupplier) params.supplier_code = filterSupplier
      if (searchTerm) params.po_number = searchTerm
      if (fromDate) params.from_date = fromDate
      if (toDate) params.to_date = toDate

      const response = await purchaseOrders.list(params)

      if (response && response.data) {
        setPOList(response.data.data || [])
        setPagination(prev => ({
          ...prev,
          total: response.data.total || 0
        }))
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (error) {
      console.error('Error fetching POs:', error)
      setPOList([])
      
      // More specific error messages for network issues
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        const errorMessage = 'Backend server not available. Please start the server on port 8000.'
        setError(errorMessage)
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to load Purchase Orders'
        setError(errorMessage)
        toast.error(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    setTitle('Purchase Orders')
    fetchPOs()
  }, [pagination.skip, filterStatus, setTitle])

  // Status badge component
  const StatusBadge = ({ status }) => {
    const statusConfig = {
      DRAFT: {
        className: 'bg-gray-100 text-gray-700',
        label: 'Draft',
        icon: FileText
      },
      SUBMITTED: {
        className: 'bg-blue-100 text-blue-700',
        label: 'Submitted',
        icon: Clock
      },
      APPROVED: {
        className: 'bg-green-100 text-green-700',
        label: 'Approved',
        icon: CheckCircle
      },
      SENT: {
        className: 'bg-purple-100 text-purple-700',
        label: 'Sent',
        icon: Package
      },
      CONFIRMED: {
        className: 'bg-indigo-100 text-indigo-700',
        label: 'Confirmed',
        icon: CheckCircle
      },
      PARTIALLY_RECEIVED: {
        className: 'bg-yellow-100 text-yellow-700',
        label: 'Partial',
        icon: Clock
      },
      RECEIVED: {
        className: 'bg-teal-100 text-teal-700',
        label: 'Received',
        icon: CheckCircle
      },
      INVOICED: {
        className: 'bg-emerald-100 text-emerald-700',
        label: 'Invoiced',
        icon: FileText
      },
      CLOSED: {
        className: 'bg-slate-100 text-slate-700',
        label: 'Closed',
        icon: CheckCircle
      },
      CANCELLED: {
        className: 'bg-red-100 text-red-700',
        label: 'Cancelled',
        icon: XCircle
      }
    }

    const config = statusConfig[status] || statusConfig.DRAFT
    const Icon = config.icon

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
        <Icon size={12} />
        {config.label}
      </span>
    )
  }

  // Delete PO
  const handleDelete = async (poNumber) => {
    if (!window.confirm(`Are you sure you want to delete PO ${poNumber}?`)) return

    try {
      await purchaseOrders.delete(poNumber)
      toast.success('PO deleted successfully')
      fetchPOs()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete PO')
    }
  }

  // Clear filters
  const clearFilters = () => {
    setSearchTerm('')
    setFilterStatus('')
    setFilterSupplier('')
    setFromDate('')
    setToDate('')
    fetchPOs()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Sticky Top Bar */}
      <div className="bg-white p-4 border-b flex flex-wrap items-center justify-between gap-4 sticky top-0 z-10">
        <div className="flex flex-wrap items-center gap-4 flex-1">
          {/* Search */}
          <div className="relative min-w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && fetchPOs()}
              placeholder="Search by PO number..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Status Filter */}
          <div className="min-w-48">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="APPROVED">Approved</option>
              <option value="SENT">Sent</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="RECEIVED">Received</option>
              <option value="INVOICED">Invoiced</option>
              <option value="CLOSED">Closed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Actions */}
        <button
          onClick={() => navigate('/purchase-orders/create')}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
        >
          <Plus size={20} />
          Create New PO
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Advanced Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* From Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                From Date
              </label>
              <input
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* To Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                To Date
              </label>
              <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Filter Actions */}
        <div className="flex items-center gap-2 mt-4">
          <button
            onClick={fetchPOs}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
          >
            <Filter size={18} />
            Apply Filters
          </button>
          <button
            onClick={clearFilters}
            className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg transition"
          >
            Clear Filters
          </button>
          <div className="ml-auto text-sm text-gray-600">
            Total: <span className="font-semibold">{pagination.total}</span> POs
          </div>
        </div>
      </div>

      {/* PO List Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading Purchase Orders...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center">
            <XCircle size={48} className="mx-auto text-red-400 mb-2" />
            <p className="text-red-600 font-medium mb-2">Error Loading Purchase Orders</p>
            <p className="text-gray-600 text-sm mb-4">{error}</p>
            <button
              onClick={fetchPOs}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
            >
              Try Again
            </button>
          </div>
        ) : poList.length === 0 ? (
          <div className="p-8 text-center">
            <Package size={48} className="mx-auto text-gray-400 mb-2" />
            <p className="text-gray-600 font-medium mb-2">No Purchase Orders Found</p>
            <p className="text-gray-500 text-sm mb-4">
              {filterStatus || searchTerm || fromDate || toDate
                ? 'Try adjusting your filters or search criteria'
                : 'Get started by creating your first purchase order'}
            </p>
            <button
              onClick={() => navigate('/purchase-orders/create')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
            >
              Create New PO
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    PO Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Supplier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Items
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {poList.map((po) => (
                  <tr key={po.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{po.po_number}</div>
                      <div className="text-xs text-gray-500">
                        By: {po.created_by}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(po.po_date).toLocaleDateString('en-IN')}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {po.supplier_name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {po.supplier_code}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={po.po_status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {po.total_items} {po.total_items === 1 ? 'item' : 'items'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-semibold text-gray-900">
                        ₹{po.grand_total?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {/* View */}
                        <button
                          onClick={() => navigate(`/purchase-orders/${po.po_number}`)}
                          className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition"
                          title="View Details"
                        >
                          <Eye size={18} />
                        </button>

                        {/* Edit (only for DRAFT) */}
                        {po.po_status === 'DRAFT' && (
                          <button
                            onClick={() => navigate(`/purchase-orders/${po.po_number}/edit`)}
                            className="p-1.5 text-green-600 hover:bg-green-50 rounded transition"
                            title="Edit PO"
                          >
                            <Edit2 size={18} />
                          </button>
                        )}

                        {/* Delete (only for DRAFT) */}
                        {po.po_status === 'DRAFT' && (
                          <button
                            onClick={() => handleDelete(po.po_number)}
                            className="p-1.5 text-red-600 hover:bg-red-50 rounded transition"
                            title="Delete PO"
                          >
                            <Trash2 size={18} />
                          </button>
                        )}

                        {/* Download */}
                        <button
                          onClick={() => toast.info('PDF download coming soon')}
                          className="p-1.5 text-gray-600 hover:bg-gray-50 rounded transition"
                          title="Download PDF"
                        >
                          <Download size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {!loading && poList.length > 0 && (
          <div className="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing <span className="font-medium">{pagination.skip + 1}</span> to{' '}
              <span className="font-medium">
                {Math.min(pagination.skip + pagination.limit, pagination.total)}
              </span>{' '}
              of <span className="font-medium">{pagination.total}</span> results
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPagination(prev => ({ ...prev, skip: Math.max(0, prev.skip - prev.limit) }))}
                disabled={pagination.skip === 0}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Previous
              </button>
              <button
                onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))}
                disabled={pagination.skip + pagination.limit >= pagination.total}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
    </div>
  )
}

export default PurchaseOrderList
