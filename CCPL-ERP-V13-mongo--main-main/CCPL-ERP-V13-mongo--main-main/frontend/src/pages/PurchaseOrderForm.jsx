import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useLayout } from '../context/LayoutContext'
import {
  Plus, Trash2, Save, X, Calculator, Package, User, MapPin,
  CreditCard, FileText, Calendar, ArrowLeft
} from 'lucide-react'
import toast from 'react-hot-toast'
import { purchaseOrders, suppliers, items as itemsAPI } from '../services/api'

const PurchaseOrderForm = () => {
  const { setTitle } = useLayout()
  const navigate = useNavigate()
  const { poNumber } = useParams()
  const isEditMode = !!poNumber

  useEffect(() => {
    setTitle(isEditMode ? 'Edit Purchase Order' : 'Create Purchase Order')
  }, [setTitle, isEditMode])

  // Form state
  const [formData, setFormData] = useState({
    po_date: new Date().toISOString().split('T')[0],
    indent_number: '',
    supplier_code: '',
    delivery_location: '',
    delivery_method: 'COURIER',
    lead_time_days: 15,
    payment_terms: 'NET 30',
    payment_method: 'BANK_TRANSFER',
    currency: 'INR',
    cost_center: '',
    project_code: '',
    department: '',
    sample_attached: false,
    remarks: '',
    terms_and_conditions: ''
  })

  const [lineItems, setLineItems] = useState([])
  const [suppliersList, setSuppliersList] = useState([])
  const [itemsList, setItemsList] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [loadError, setLoadError] = useState(null)

  // Calculated summary
  const [summary, setSummary] = useState({
    subtotal: 0,
    total_discount: 0,
    total_taxable: 0,
    total_gst: 0,
    grand_total: 0
  })

  // Fetch suppliers
  useEffect(() => {
    const fetchSuppliers = async () => {
      try {
        const response = await suppliers.list()
        if (response && response.data) {
          // Handle both array and paginated response formats
          const supplierData = Array.isArray(response.data)
            ? response.data
            : (response.data.data || response.data.items || [])
          setSuppliersList(supplierData)
        }
      } catch (error) {
        console.error('Error fetching suppliers:', error)
        // Set empty array to prevent form from breaking
        setSuppliersList([])
        const errorMsg = 'Backend server not available. Please start the server first.'
        setLoadError(errorMsg)
        // Don't show toast error for initial load failures
      }
    }
    fetchSuppliers()
  }, [])

  // Fetch items
  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await itemsAPI.list()
        if (response && response.data) {
          // Handle both array and paginated response formats
          const itemData = Array.isArray(response.data)
            ? response.data
            : (response.data.data || response.data.items || [])
          setItemsList(itemData)
        }
      } catch (error) {
        console.error('Error fetching items:', error)
        // Set empty array to prevent form from breaking
        setItemsList([])
        const errorMsg = 'Backend server not available. Please start the server first.'
        setLoadError(errorMsg)
        // Don't show toast error for initial load failures
      }
    }
    fetchItems()
  }, [])

  // Calculate line item amounts
  const calculateLineItem = (item) => {
    const lineAmount = item.quantity * item.unit_rate
    const discountAmount = lineAmount * (item.discount_percent / 100)
    const taxableAmount = lineAmount - discountAmount
    const gstAmount = taxableAmount * (item.gst_percent / 100)
    const netAmount = taxableAmount + gstAmount

    return {
      ...item,
      line_amount: lineAmount,
      discount_amount: discountAmount,
      taxable_amount: taxableAmount,
      gst_amount: gstAmount,
      net_amount: netAmount
    }
  }

  // Recalculate summary
  useEffect(() => {
    const calculatedItems = lineItems.map(calculateLineItem)

    const subtotal = calculatedItems.reduce((sum, item) => sum + item.line_amount, 0)
    const totalDiscount = calculatedItems.reduce((sum, item) => sum + item.discount_amount, 0)
    const totalTaxable = calculatedItems.reduce((sum, item) => sum + item.taxable_amount, 0)
    const totalGst = calculatedItems.reduce((sum, item) => sum + item.gst_amount, 0)
    const grandTotal = Math.round(totalTaxable + totalGst)

    setSummary({
      subtotal: subtotal.toFixed(2),
      total_discount: totalDiscount.toFixed(2),
      total_taxable: totalTaxable.toFixed(2),
      total_gst: totalGst.toFixed(2),
      grand_total: grandTotal
    })
  }, [lineItems])

  // Add new line item
  const addLineItem = () => {
    const newItem = {
      id: Date.now(),
      item_code: '',
      item_name: '',
      item_description: '',
      item_category: '',
      quantity: 1,
      unit: 'PCS',
      unit_rate: 0,
      discount_percent: 0,
      hsn_code: '',
      gst_percent: 18,
      expected_delivery_date: '',
      inspection_required: false,
      quality_specs: '',
      notes: ''
    }
    setLineItems([...lineItems, newItem])
  }

  // Remove line item
  const removeLineItem = (id) => {
    setLineItems(lineItems.filter(item => item.id !== id))
  }

  // Update line item
  const updateLineItem = (id, field, value) => {
    setLineItems(lineItems.map(item =>
      item.id === id ? { ...item, [field]: value } : item
    ))
  }

  // Handle item selection from dropdown
  const handleItemSelect = (id, itemCode) => {
    const selectedItem = itemsList.find(i => i.code === itemCode)
    if (selectedItem) {
      updateLineItem(id, 'item_code', selectedItem.code)
      updateLineItem(id, 'item_name', selectedItem.name)
      updateLineItem(id, 'item_description', selectedItem.description || '')
      updateLineItem(id, 'hsn_code', selectedItem.hsn_code || '')
      updateLineItem(id, 'gst_percent', selectedItem.gst_rate || 18)
      updateLineItem(id, 'unit', selectedItem.unit || 'PCS')
    }
  }

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault()

    // Validation
    if (!formData.supplier_code) {
      toast.error('Please select a supplier')
      return
    }

    if (lineItems.length === 0) {
      toast.error('Please add at least one item')
      return
    }

    if (lineItems.some(item => !item.item_code || item.quantity <= 0 || item.unit_rate <= 0)) {
      toast.error('Please fill all item details correctly')
      return
    }

    if (!formData.delivery_location) {
      toast.error('Please enter delivery location')
      return
    }

    setSaving(true)

    try {
      const payload = {
        ...formData,
        items: lineItems.map(item => ({
          item_code: item.item_code,
          item_name: item.item_name,
          item_description: item.item_description,
          item_category: item.item_category,
          quantity: parseFloat(item.quantity),
          unit: item.unit,
          unit_rate: parseFloat(item.unit_rate),
          discount_percent: parseFloat(item.discount_percent || 0),
          hsn_code: item.hsn_code,
          gst_percent: parseFloat(item.gst_percent || 0),
          expected_delivery_date: item.expected_delivery_date || null,
          inspection_required: item.inspection_required,
          quality_specs: item.quality_specs,
          notes: item.notes
        }))
      }

      if (isEditMode) {
        await purchaseOrders.update(poNumber, payload)
        toast.success('Purchase Order updated successfully')
      } else {
        const response = await purchaseOrders.create(payload)
        toast.success(`Purchase Order ${response.data.po_number} created successfully`)
        navigate(`/purchase-orders/${response.data.po_number}`)
      }
    } catch (error) {
      console.error('Error saving PO:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to save Purchase Order'
      setError(errorMsg)
      toast.error(errorMsg)
    } finally {
      setSaving(false)
    }
  }

  // Show error state if load failed
  if (loadError) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <X size={48} className="mx-auto text-red-400 mb-4" />
            <h2 className="text-xl font-semibold text-red-600 mb-2">Error Loading Form</h2>
            <p className="text-gray-600 mb-4">{loadError}</p>
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
             <h1 className="text-xl font-bold text-gray-900">
               {isEditMode ? `Edit PO #${poNumber}` : 'New Purchase Order'}
             </h1>
             <p className="text-xs text-gray-500">
               {isEditMode ? 'Update purchase order details' : 'Create a new purchase order'}
             </p>
           </div>
        </div>

        <div className="flex items-center gap-2">
           <button 
             type="button"
             onClick={() => navigate('/purchase-orders')}
             className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm font-medium"
           >
             Cancel
           </button>
           <button
             onClick={handleSubmit}
             disabled={saving || lineItems.length === 0}
             className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium shadow-sm"
           >
             {saving ? (
               <>
                 <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                 Saving...
               </>
             ) : (
               <>
                 <Save size={18} />
                 {isEditMode ? 'Update PO' : 'Create PO'}
               </>
             )}
           </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          {/* Error Display */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-2">
                <X size={20} />
                <span>{error}</span>
              </div>
              <button onClick={() => setError(null)} className="text-red-700 hover:text-red-900">
                <X size={18} />
              </button>
            </div>
          )}

          {/* Load Error Display */}
          {loadError && (
            <div className="mb-6 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg">
              <div className="flex items-center gap-2">
                <Package size={20} />
                <div>
                  <p className="font-medium">Unable to load required data</p>
                  <p className="text-sm mt-1">{loadError}</p>
                  <p className="text-sm mt-1">Please ensure the backend server is running on port 8000.</p>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
        {/* PO Header Information */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText size={20} className="text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">PO Information</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                PO Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.po_date}
                onChange={(e) => setFormData({ ...formData, po_date: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Indent Number
              </label>
              <input
                type="text"
                value={formData.indent_number}
                onChange={(e) => setFormData({ ...formData, indent_number: e.target.value })}
                placeholder="INDENT-001"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Supplier <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.supplier_code}
                onChange={(e) => setFormData({ ...formData, supplier_code: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select Supplier</option>
                {suppliersList.map((supplier) => (
                  <option key={supplier.id} value={supplier.code}>
                    {supplier.company_name} ({supplier.code})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Line Items */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Package size={20} className="text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">Line Items</h2>
            </div>
            <button
              type="button"
              onClick={addLineItem}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
            >
              <Plus size={18} />
              Add Item
            </button>
          </div>

          {lineItems.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Package size={48} className="mx-auto mb-2 text-gray-400" />
              <p>No items added yet. Click "Add Item" to get started.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {lineItems.map((item, index) => (
                <div key={item.id} className="border border-gray-200 rounded-lg p-4 relative">
                  {/* Remove button */}
                  <button
                    type="button"
                    onClick={() => removeLineItem(item.id)}
                    className="absolute top-2 right-2 p-1 text-red-600 hover:bg-red-50 rounded transition"
                  >
                    <Trash2 size={18} />
                  </button>

                  <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                    {/* Item Selection */}
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Item <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={item.item_code}
                        onChange={(e) => handleItemSelect(item.id, e.target.value)}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Select Item</option>
                        {itemsList.map((itm) => (
                          <option key={itm.id} value={itm.code}>
                            {itm.name} ({itm.code})
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Quantity */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Quantity <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => updateLineItem(item.id, 'quantity', e.target.value)}
                        min="0.01"
                        step="0.01"
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    {/* Unit */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Unit
                      </label>
                      <select
                        value={item.unit}
                        onChange={(e) => updateLineItem(item.id, 'unit', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="PCS">PCS</option>
                        <option value="KG">KG</option>
                        <option value="MTR">MTR</option>
                        <option value="LTR">LTR</option>
                        <option value="BOX">BOX</option>
                        <option value="SET">SET</option>
                      </select>
                    </div>

                    {/* Unit Rate */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Rate (₹) <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        value={item.unit_rate}
                        onChange={(e) => updateLineItem(item.id, 'unit_rate', e.target.value)}
                        min="0"
                        step="0.01"
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    {/* Discount % */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Disc. %
                      </label>
                      <input
                        type="number"
                        value={item.discount_percent}
                        onChange={(e) => updateLineItem(item.id, 'discount_percent', e.target.value)}
                        min="0"
                        max="100"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>

                  {/* Additional Fields Row */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        HSN Code
                      </label>
                      <input
                        type="text"
                        value={item.hsn_code}
                        onChange={(e) => updateLineItem(item.id, 'hsn_code', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        GST %
                      </label>
                      <input
                        type="number"
                        value={item.gst_percent}
                        onChange={(e) => updateLineItem(item.id, 'gst_percent', e.target.value)}
                        min="0"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Expected Delivery
                      </label>
                      <input
                        type="date"
                        value={item.expected_delivery_date}
                        onChange={(e) => updateLineItem(item.id, 'expected_delivery_date', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div className="flex items-end">
                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={item.inspection_required}
                          onChange={(e) => updateLineItem(item.id, 'inspection_required', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        Inspection Required
                      </label>
                    </div>
                  </div>

                  {/* Calculated Amounts Display */}
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="grid grid-cols-5 gap-2 text-sm">
                      <div>
                        <span className="text-gray-600">Amount:</span>
                        <span className="ml-1 font-medium">₹{calculateLineItem(item).line_amount.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Discount:</span>
                        <span className="ml-1 font-medium">₹{calculateLineItem(item).discount_amount.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Taxable:</span>
                        <span className="ml-1 font-medium">₹{calculateLineItem(item).taxable_amount.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">GST:</span>
                        <span className="ml-1 font-medium">₹{calculateLineItem(item).gst_amount.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Total:</span>
                        <span className="ml-1 font-semibold text-blue-600">₹{calculateLineItem(item).net_amount.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Summary */}
          {lineItems.length > 0 && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <Calculator size={20} className="text-blue-600" />
                <h3 className="font-semibold text-gray-900">Order Summary</h3>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Subtotal</div>
                  <div className="text-lg font-semibold text-gray-900">₹{summary.subtotal}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Discount</div>
                  <div className="text-lg font-semibold text-red-600">-₹{summary.total_discount}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Taxable</div>
                  <div className="text-lg font-semibold text-gray-900">₹{summary.total_taxable}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Total GST</div>
                  <div className="text-lg font-semibold text-gray-900">₹{summary.total_gst}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Grand Total</div>
                  <div className="text-2xl font-bold text-blue-600">₹{summary.grand_total.toLocaleString('en-IN')}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Delivery Information */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <MapPin size={20} className="text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Delivery Information</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delivery Location <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.delivery_location}
                onChange={(e) => setFormData({ ...formData, delivery_location: e.target.value })}
                placeholder="Warehouse A"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delivery Method
              </label>
              <select
                value={formData.delivery_method}
                onChange={(e) => setFormData({ ...formData, delivery_method: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="COURIER">Courier</option>
                <option value="FOB">FOB</option>
                <option value="CIF">CIF</option>
                <option value="PICKUP">Pickup</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lead Time (Days)
              </label>
              <input
                type="number"
                value={formData.lead_time_days}
                onChange={(e) => setFormData({ ...formData, lead_time_days: e.target.value })}
                min="1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Payment Information */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <CreditCard size={20} className="text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Payment Information</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Terms
              </label>
              <select
                value={formData.payment_terms}
                onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="NET 30">NET 30</option>
                <option value="NET 45">NET 45</option>
                <option value="NET 60">NET 60</option>
                <option value="COD">COD</option>
                <option value="ADVANCE">Advance</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Method
              </label>
              <select
                value={formData.payment_method}
                onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="BANK_TRANSFER">Bank Transfer</option>
                <option value="CHEQUE">Cheque</option>
                <option value="CASH">Cash</option>
                <option value="CREDIT_CARD">Credit Card</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Currency
              </label>
              <select
                value={formData.currency}
                onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Additional Information */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Information</h2>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cost Center
                </label>
                <input
                  type="text"
                  value={formData.cost_center}
                  onChange={(e) => setFormData({ ...formData, cost_center: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Code
                </label>
                <input
                  type="text"
                  value={formData.project_code}
                  onChange={(e) => setFormData({ ...formData, project_code: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <input
                  type="text"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={formData.sample_attached}
                  onChange={(e) => setFormData({ ...formData, sample_attached: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                Sample Attached
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Remarks
              </label>
              <textarea
                value={formData.remarks}
                onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Terms & Conditions
              </label>
              <textarea
                value={formData.terms_and_conditions}
                onChange={(e) => setFormData({ ...formData, terms_and_conditions: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

      </form>
        </div>
      </div>
    </div>
  )
}

export default PurchaseOrderForm
