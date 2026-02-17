import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useLayout } from '../context/LayoutContext'
import {
  ArrowLeft, Edit2, Download, FileText, User, MapPin,
  Calendar, Package, CreditCard, CheckCircle, XCircle
} from 'lucide-react'
import toast from 'react-hot-toast'
import { purchaseOrders } from '../services/api'

const PurchaseOrderDetail = () => {
  const { setTitle } = useLayout()
  const navigate = useNavigate()
  const { poNumber } = useParams()

  const [po, setPO] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setTitle('Purchase Order Details')
  }, [setTitle])

  // Fetch PO details
  useEffect(() => {
    const fetchPODetails = async () => {
      if (!poNumber) {
        setError('No PO number provided')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const response = await purchaseOrders.get(poNumber)
        setPO(response.data)
        setError(null)
      } catch (error) {
        console.error('Error fetching PO:', error)
        const errorMsg = error.response?.data?.detail || 'Failed to load Purchase Order'
        setError(errorMsg)
        toast.error(errorMsg)
      } finally {
        setLoading(false)
      }
    }

    fetchPODetails()
  }, [poNumber])

  // Status badge component
  const StatusBadge = ({ status }) => {
    const statusConfig = {
      DRAFT: { className: 'bg-gray-100 text-gray-700', label: 'Draft' },
      SUBMITTED: { className: 'bg-blue-100 text-blue-700', label: 'Submitted' },
      APPROVED: { className: 'bg-green-100 text-green-700', label: 'Approved' },
      SENT: { className: 'bg-purple-100 text-purple-700', label: 'Sent' },
      CONFIRMED: { className: 'bg-indigo-100 text-indigo-700', label: 'Confirmed' },
      PARTIALLY_RECEIVED: { className: 'bg-yellow-100 text-yellow-700', label: 'Partial' },
      RECEIVED: { className: 'bg-teal-100 text-teal-700', label: 'Received' },
      INVOICED: { className: 'bg-emerald-100 text-emerald-700', label: 'Invoiced' },
      CLOSED: { className: 'bg-slate-100 text-slate-700', label: 'Closed' },
      CANCELLED: { className: 'bg-red-100 text-red-700', label: 'Cancelled' }
    }

    const config = statusConfig[status] || statusConfig.DRAFT

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.className}`}>
        {config.label}
      </span>
    )
  }

  // Loading state
  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading Purchase Order...</span>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <XCircle size={48} className="mx-auto text-red-400 mb-4" />
            <h2 className="text-xl font-semibold text-red-600 mb-2">Error Loading Purchase Order</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => window.location.reload()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
              >
                Retry
              </button>
              <button
                onClick={() => navigate('/purchase-orders')}
                className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg transition"
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // No PO found
  if (!po) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <FileText size={48} className="mx-auto text-gray-400 mb-4" />
            <h2 className="text-xl font-semibold text-gray-600 mb-2">Purchase Order Not Found</h2>
            <p className="text-gray-500 mb-4">The purchase order you're looking for doesn't exist.</p>
            <button
              onClick={() => navigate('/purchase-orders')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
            >
              Back to Purchase Orders
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Sticky Top Bar */}
      <div className="bg-white p-4 border-b flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/purchase-orders')}
            className="p-2 hover:bg-gray-100 rounded-full transition"
          >
            <ArrowLeft size={20} className="text-gray-600" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-900">PO #{po.po_number}</h1>
            <div className="flex items-center gap-2 mt-1">
               <StatusBadge status={po.po_status} />
               <span className="text-xs text-gray-500">Created on {new Date(po.po_date).toLocaleDateString('en-IN')}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {po.po_status === 'DRAFT' && (
            <button
              onClick={() => navigate(`/purchase-orders/${po.po_number}/edit`)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition text-sm font-medium shadow-sm"
            >
              <Edit2 size={16} />
              Edit
            </button>
          )}
          <button
            onClick={() => toast.info('PDF download coming soon')}
            className="flex items-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg transition text-sm font-medium"
          >
            <Download size={16} />
            Download PDF
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          {/* PO Information */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Supplier Info */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <User size={20} className="text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Supplier Details</h2>
          </div>
          <div className="space-y-2">
            <div>
              <span className="text-sm text-gray-500">Company Name</span>
              <p className="font-medium text-gray-900">{po.supplier_name || 'N/A'}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Supplier Code</span>
              <p className="font-medium text-gray-900">{po.supplier_code}</p>
            </div>
          </div>
        </div>

        {/* Order Info */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calendar size={20} className="text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Order Information</h2>
          </div>
          <div className="space-y-2">
            <div>
              <span className="text-sm text-gray-500">PO Date</span>
              <p className="font-medium text-gray-900">
                {new Date(po.po_date).toLocaleDateString('en-IN')}
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Indent Number</span>
              <p className="font-medium text-gray-900">{po.indent_number || 'N/A'}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Created By</span>
              <p className="font-medium text-gray-900">{po.created_by}</p>
            </div>
          </div>
        </div>

        {/* Delivery Info */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <MapPin size={20} className="text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Delivery Details</h2>
          </div>
          <div className="space-y-2">
            <div>
              <span className="text-sm text-gray-500">Location</span>
              <p className="font-medium text-gray-900">{po.delivery_location}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Method</span>
              <p className="font-medium text-gray-900">{po.delivery_method}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Lead Time</span>
              <p className="font-medium text-gray-900">{po.lead_time_days} days</p>
            </div>
          </div>
        </div>
      </div>

      {/* Line Items */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Package size={20} className="text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">Line Items</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item Code</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item Name</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Unit</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Rate</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Disc %</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">GST %</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {po.items && po.items.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">{index + 1}</td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.item_code}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    <div>{item.item_name}</div>
                    {item.item_description && (
                      <div className="text-xs text-gray-500">{item.item_description}</div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-900">{item.quantity}</td>
                  <td className="px-4 py-3 text-sm text-right text-gray-900">{item.unit}</td>
                  <td className="px-4 py-3 text-sm text-right text-gray-900">
                    ₹{item.unit_rate.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-900">
                    {item.discount_percent || 0}%
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-900">
                    {item.gst_percent || 0}%
                  </td>
                  <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                    ₹{item.net_amount?.toFixed(2) || '0.00'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Summary */}
        <div className="mt-6 flex justify-end">
          <div className="w-full max-w-md space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Subtotal:</span>
              <span className="font-medium">₹{po.subtotal?.toFixed(2) || '0.00'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Discount:</span>
              <span className="font-medium text-red-600">-₹{po.total_discount?.toFixed(2) || '0.00'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Taxable Amount:</span>
              <span className="font-medium">₹{po.total_taxable?.toFixed(2) || '0.00'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Total GST:</span>
              <span className="font-medium">₹{po.total_gst?.toFixed(2) || '0.00'}</span>
            </div>
            <div className="flex justify-between text-lg font-bold border-t pt-2">
              <span className="text-gray-900">Grand Total:</span>
              <span className="text-blue-600">₹{po.grand_total?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) || '0.00'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Information */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <CreditCard size={20} className="text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">Payment Information</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <span className="text-sm text-gray-500">Payment Terms</span>
            <p className="font-medium text-gray-900">{po.payment_terms}</p>
          </div>
          <div>
            <span className="text-sm text-gray-500">Payment Method</span>
            <p className="font-medium text-gray-900">{po.payment_method}</p>
          </div>
          <div>
            <span className="text-sm text-gray-500">Currency</span>
            <p className="font-medium text-gray-900">{po.currency}</p>
          </div>
        </div>
      </div>

      {/* Additional Information */}
      {(po.remarks || po.terms_and_conditions) && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Information</h2>
          {po.remarks && (
            <div className="mb-4">
              <span className="text-sm text-gray-500 block mb-1">Remarks</span>
              <p className="text-gray-900">{po.remarks}</p>
            </div>
          )}
          {po.terms_and_conditions && (
            <div>
              <span className="text-sm text-gray-500 block mb-1">Terms & Conditions</span>
              <p className="text-gray-900 whitespace-pre-line">{po.terms_and_conditions}</p>
            </div>
          )}
        </div>
      )}
        </div>
      </div>
    </div>
  )
}

export default PurchaseOrderDetail
