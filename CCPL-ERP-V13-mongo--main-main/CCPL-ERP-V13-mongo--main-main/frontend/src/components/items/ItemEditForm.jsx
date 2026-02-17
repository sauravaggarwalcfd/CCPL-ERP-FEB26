import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import toast from 'react-hot-toast'
import { items as itemsApi, categoryHierarchy } from '../../services/api'

export default function ItemEditForm({ isOpen, onClose, onSuccess, item, variant = 'modal' }) {
  const [formData, setFormData] = useState({
    item_code: '',
    item_name: '',
    item_type: '',
    category_id: '',
    sub_category_id: '',
    division_id: '',
    class_id: '',
    sub_class_id: '',
    brand: '',
    model: '',
    size: '',
    color: '',
    unit: '',
    hsn_sac: '',
    gst_rate: '',
    purchase_price: '',
    selling_price: '',
    mrp: '',
    description: '',
    status: 'active'
  })

  const [categories, setCategories] = useState([])
  const [subCategories, setSubCategories] = useState([])
  const [divisions, setDivisions] = useState([])
  const [classes, setClasses] = useState([])
  const [subClasses, setSubClasses] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && item) {
      // Populate form with item data
      setFormData({
        item_code: item.item_code || '',
        item_name: item.item_name || '',
        item_type: item.item_type || '',
        category_id: item.category_id || '',
        sub_category_id: item.sub_category_id || '',
        division_id: item.division_id || '',
        class_id: item.class_id || '',
        sub_class_id: item.sub_class_id || '',
        brand: item.brand || '',
        model: item.model || '',
        size: item.size || '',
        color: item.color || '',
        unit: item.unit || '',
        hsn_sac: item.hsn_sac || '',
        gst_rate: item.gst_rate || '',
        purchase_price: item.purchase_price || '',
        selling_price: item.selling_price || '',
        mrp: item.mrp || '',
        description: item.description || '',
        status: item.status || 'active'
      })
      
      fetchCategories()
      
      // Load dropdowns based on existing selections
      if (item.category_id) {
        fetchSubCategories(item.category_id)
      }
      if (item.sub_category_id) {
        fetchDivisions(item.sub_category_id)
      }
      if (item.division_id) {
        fetchClasses(item.division_id)
      }
      if (item.class_id) {
        fetchSubClasses(item.class_id)
      }
    }
  }, [isOpen, item])

  const fetchCategories = async () => {
    try {
      const response = await categoryHierarchy.getCategories()
      setCategories(response.data || [])
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    }
  }

  const fetchSubCategories = async (categoryId) => {
    try {
      const response = await categoryHierarchy.getSubCategories(categoryId)
      setSubCategories(response.data || [])
    } catch (error) {
      console.error('Failed to fetch sub-categories:', error)
    }
  }

  const fetchDivisions = async (subCategoryId) => {
    try {
      const response = await categoryHierarchy.getDivisions(subCategoryId)
      setDivisions(response.data || [])
    } catch (error) {
      console.error('Failed to fetch divisions:', error)
    }
  }

  const fetchClasses = async (divisionId) => {
    try {
      const response = await categoryHierarchy.getClasses(divisionId)
      setClasses(response.data || [])
    } catch (error) {
      console.error('Failed to fetch classes:', error)
    }
  }

  const fetchSubClasses = async (classId) => {
    try {
      const response = await categoryHierarchy.getSubClasses(classId)
      setSubClasses(response.data || [])
    } catch (error) {
      console.error('Failed to fetch sub-classes:', error)
    }
  }

  const handleCategoryChange = (e) => {
    const categoryId = e.target.value
    setFormData({
      ...formData,
      category_id: categoryId,
      sub_category_id: '',
      division_id: '',
      class_id: '',
      sub_class_id: ''
    })
    setSubCategories([])
    setDivisions([])
    setClasses([])
    setSubClasses([])
    if (categoryId) {
      fetchSubCategories(categoryId)
    }
  }

  const handleSubCategoryChange = (e) => {
    const subCategoryId = e.target.value
    setFormData({
      ...formData,
      sub_category_id: subCategoryId,
      division_id: '',
      class_id: '',
      sub_class_id: ''
    })
    setDivisions([])
    setClasses([])
    setSubClasses([])
    if (subCategoryId) {
      fetchDivisions(subCategoryId)
    }
  }

  const handleDivisionChange = (e) => {
    const divisionId = e.target.value
    setFormData({
      ...formData,
      division_id: divisionId,
      class_id: '',
      sub_class_id: ''
    })
    setClasses([])
    setSubClasses([])
    if (divisionId) {
      fetchClasses(divisionId)
    }
  }

  const handleClassChange = (e) => {
    const classId = e.target.value
    setFormData({
      ...formData,
      class_id: classId,
      sub_class_id: ''
    })
    setSubClasses([])
    if (classId) {
      fetchSubClasses(classId)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await itemsApi.update(item.item_code, formData)
      toast.success('Item updated successfully!')
      onSuccess()
      onClose()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update item')
      console.error('Update error:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  // Panel variant: render inline within sidebar
  if (variant === 'panel') {
    return (
      <div className="bg-white rounded-lg shadow-md w-full h-full overflow-y-auto flex flex-col">
        <div className="bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">Edit Item</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Item Code (Read-only) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Item Code <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.item_code}
              disabled
              className="w-full px-3 py-2 border rounded-md bg-gray-100 text-gray-600"
            />
          </div>

          {/* Item Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Item Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="item_name"
              value={formData.item_name}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category Hierarchy */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.category_id}
                onChange={handleCategoryChange}
                required
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Category</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sub-Category <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.sub_category_id}
                onChange={handleSubCategoryChange}
                required
                disabled={!formData.category_id}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select Sub-Category</option>
                {subCategories.map(sub => (
                  <option key={sub.id} value={sub.id}>{sub.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Division <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.division_id}
                onChange={handleDivisionChange}
                required
                disabled={!formData.sub_category_id}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select Division</option>
                {divisions.map(div => (
                  <option key={div.id} value={div.id}>{div.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Class <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.class_id}
                onChange={handleClassChange}
                required
                disabled={!formData.division_id}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select Class</option>
                {classes.map(cls => (
                  <option key={cls.id} value={cls.id}>{cls.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sub-Class <span className="text-red-500">*</span>
              </label>
              <select
                name="sub_class_id"
                value={formData.sub_class_id}
                onChange={handleInputChange}
                required
                disabled={!formData.class_id}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select Sub-Class</option>
                {subClasses.map(subCls => (
                  <option key={subCls.id} value={subCls.id}>{subCls.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Product Details */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Brand</label>
              <input
                type="text"
                name="brand"
                value={formData.brand}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
              <input
                type="text"
                name="model"
                value={formData.model}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Size</label>
              <input
                type="text"
                name="size"
                value={formData.size}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Color</label>
              <input
                type="text"
                name="color"
                value={formData.color}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
              <input
                type="text"
                name="unit"
                value={formData.unit}
                onChange={handleInputChange}
                placeholder="e.g., PCS, KG, LITER"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">HSN/SAC</label>
              <input
                type="text"
                name="hsn_sac"
                value={formData.hsn_sac}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">GST Rate (%)</label>
              <input
                type="number"
                name="gst_rate"
                value={formData.gst_rate}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Pricing */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Purchase Price</label>
              <input
                type="number"
                name="purchase_price"
                value={formData.purchase_price}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Selling Price</label>
              <input
                type="number"
                name="selling_price"
                value={formData.selling_price}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">MRP</label>
              <input
                type="number"
                name="mrp"
                value={formData.mrp}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Updating...' : 'Update Item'}
            </button>
          </div>
        </form>
      </div>
    )
  }

  // Default modal variant
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">Edit Item</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Item Code (Read-only) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Item Code <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.item_code}
              disabled
              className="w-full px-3 py-2 border rounded-md bg-gray-100 text-gray-600"
            />
          </div>
          
          {/* Item Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Item Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="item_name"
              value={formData.item_name}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category Hierarchy */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.category_id}
                onChange={handleCategoryChange}
                required
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Category</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text sm font-medium text-gray-700 mb-2">
                Sub-Category <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.sub_category_id}
                onChange={handleSubCategoryChange}
                required
                disabled={!formData.category_id}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select Sub-Category</option>
                {subCategories.map(sub => (
                  <option key={sub.id} value={sub.id}>{sub.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Division <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.division_id}
                onChange={handleDivisionChange}
                required
                disabled={!formData.sub_category_id}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select Division</option>
                {divisions.map(div => (
                  <option key={div.id} value={div.id}>{div.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Class <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.class_id}
                onChange={handleClassChange}
                required
                disabled={!formData.division_id}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select Class</option>
                {classes.map(cls => (
                  <option key={cls.id} value={cls.id}>{cls.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sub-Class <span className="text-red-500">*</span>
              </label>
              <select
                name="sub_class_id"
                value={formData.sub_class_id}
                onChange={handleInputChange}
                required
                disabled={!formData.class_id}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select Sub-Class</option>
                {subClasses.map(subCls => (
                  <option key={subCls.id} value={subCls.id}>{subCls.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Product Details */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Brand</label>
              <input
                type="text"
                name="brand"
                value={formData.brand}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
              <input
                type="text"
                name="model"
                value={formData.model}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Size</label>
              <input
                type="text"
                name="size"
                value={formData.size}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Color</label>
              <input
                type="text"
                name="color"
                value={formData.color}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
              <input
                type="text"
                name="unit"
                value={formData.unit}
                onChange={handleInputChange}
                placeholder="e.g., PCS, KG, LITER"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">HSN/SAC</label>
              <input
                type="text"
                name="hsn_sac"
                value={formData.hsn_sac}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">GST Rate (%)</label>
              <input
                type="number"
                name="gst_rate"
                value={formData.gst_rate}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Pricing */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Purchase Price</label>
              <input
                type="number"
                name="purchase_price"
                value={formData.purchase_price}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Selling Price</label>
              <input
                type="number"
                name="selling_price"
                value={formData.selling_price}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">MRP</label>
              <input
                type="number"
                name="mrp"
                value={formData.mrp}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Updating...' : 'Update Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
