import { useState, useEffect } from 'react'
import { Plus, ChevronRight, ChevronDown, Trash2, FolderTree, FolderOpen, Folder, Package, Settings, X, Eye } from 'lucide-react'
import toast from 'react-hot-toast'
import { useLayout } from '../context/LayoutContext'

export default function ItemCategoryEnhanced() {
  const { setTitle } = useLayout()
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [expandedNodes, setExpandedNodes] = useState(new Set())
  const [editMode, setEditMode] = useState(false) // false = create, true = edit
  const [activeTab, setActiveTab] = useState('all')
  
  // Preview state
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState(null)
  const [previewType, setPreviewType] = useState('') // 'all', 'level1', 'level2', 'level3'
  
  // Enum options
  const [inventoryClasses, setInventoryClasses] = useState([])
  const [unitsOfMeasure, setUnitsOfMeasure] = useState([])
  const [filterStatus, setFilterStatus] = useState('all') // all, active, inactive
  const [filterClass, setFilterClass] = useState('all')

  const [formData, setFormData] = useState({
    category_name: '',
    category_code: '',
    description: '',
    parent_category_id: null,
    parent_category_name: null,
    level: 1,
    inventory_class: null,
    default_uom: null,
    waste_percentage: 0,
    reorder_point: null,
    lead_time_days: null,
    preferred_supplier_id: null,
    preferred_supplier_name: '',
    standard_cost: null,
    requires_batch_tracking: false,
    requires_expiry_tracking: false,
    quality_check_required: false,
    storage_requirements: '',
    handling_instructions: '',
    sort_order: 0,
    is_active: true,
  })

  useEffect(() => {
    setTitle('Enhanced Category Master')
    fetchCategories()
    fetchEnums()
  }, [setTitle])

  const getToken = () => localStorage.getItem('access_token')

  const fetchEnums = async () => {
    try {
      const [classesRes, uomRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/items/enums/inventory-classes', {
          headers: { 'Authorization': `Bearer ${getToken()}` }
        }),
        fetch('http://127.0.0.1:8000/api/items/enums/units-of-measure', {
          headers: { 'Authorization': `Bearer ${getToken()}` }
        })
      ])
      
      setInventoryClasses(await classesRes.json())
      setUnitsOfMeasure(await uomRes.json())
    } catch (error) {
      console.error('Failed to fetch enums', error)
    }
  }

  const fetchCategories = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://127.0.0.1:8000/api/items/categories?limit=1000', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      })
      const data = await response.json()
      setCategories(Array.isArray(data) ? data : [])
    } catch (error) {
      toast.error('Failed to fetch categories')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      category_name: '',
      category_code: '',
      description: '',
      parent_category_id: null,
      parent_category_name: null,
      level: 1,
      inventory_class: null,
      default_uom: null,
      waste_percentage: 0,
      reorder_point: null,
      lead_time_days: null,
      preferred_supplier_id: null,
      preferred_supplier_name: '',
      standard_cost: null,
      requires_batch_tracking: false,
      requires_expiry_tracking: false,
      quality_check_required: false,
      storage_requirements: '',
      handling_instructions: '',
      is_active: true,
    })
    setEditMode(false)
    setSelecteSaveCategory = async (e) => {
    e.preventDefault()
    
    if (!formData.category_name || !formData.category_code) {
      toast.error('Category name and code are required')
      return
    }

    try {
      const categoryData = {
        category_id: formData.category_code.toUpperCase(),
        ...formData
      }

      if (editMode && selectedCategory) {
        // Update existing category
        const response = await fetch(`http://127.0.0.1:8000/api/items/categories/${selectedCategory.category_id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
          },
          body: JSON.stringify(categoryData)
        })

        if (response.ok) {
          toast.success('Category updated successfully!')
          resetForm()
          fetchCategories()
        } else {
          const error = await response.json()
          toast.error(error.detail || 'Failed to update category')
        }
      } else {
        // Create new category
        const response = await fetch('http://127.0.0.1:8000/api/items/categories', {
          method: 'POST',
          headers: {
            'CEditCategory = (category) => {
    setSelectedCategory(category)
    setEditMode(true)
    setFormData({
      category_name: category.category_name,
      category_code: category.category_code,
      description: category.description || '',
      parent_category_id: category.parent_category_id,
      parent_category_name: category.parent_category_name || '',
      level: category.level,
      inventory_class: category.inventory_class,
      default_uom: category.default_uom,
      waste_percentage: category.waste_percentage || 0,
      reorder_point: category.reorder_point,
      lead_time_days: category.lead_time_days,
      preferred_supplier_id: category.preferred_supplier_id,
      preferred_supplier_name: category.preferred_supplier_name || '',
      standard_cost: category.standard_cost,
      requires_batch_tracking: category.requires_batch_tracking || false,
      requires_expiry_tracking: category.requires_expiry_tracking || false,
      quality_check_required: category.quality_check_required || false,
      storage_requirements: category.storage_requirements || '',
      handling_instructions: category.handling_instructions || '',
      sort_order: category.sort_order || 0,
      is_active: category.is_active !== false,
    })
  }

  const handleAddNewCategory = () => {
    resetForm()
    setEditMode(false)
    setSelectedCategory(null)
  }

  // Preview functionality
  const handleTabPreview = (tabKey) => {
    const filteredData = categories.filter(cat => {
      if (tabKey === 'all') return true
      if (tabKey === 'level1') return cat.level === 1
      if (tabKey === 'level2') return cat.level === 2
      if (tabKey === 'level3') return cat.level === 3
      return true
    })

    const titles = {
      'all': 'All Categories Preview',
      'level1': 'Level 1 - Inventory Class Preview',
      'level2': 'Level 2 - Material Type Preview',
      'level3': 'Level 3 - Sub-Category Preview'
    }

    setPreviewType(tabKey)
    setPreviewData(filteredData)
    setShowPreview(true)
  }

  const closePreview = () => {
    setShowPreview(false)
    setPreviewData(null)
    setPreviewType('')
  }toggleNode = (categoryId) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId)
    } else {
      newExpanded.add(categoryId)
    }
    setExpandedNodes(newExpanded))
    setShowEditModal(true)
  }

  const handleUpdateCategory = async (e) => {
    e.preventDefault()
    
    if (!formData.category_name || !formData.category_code) {
      toast.error('Category name and code are required')
      return
    }

    try {
      const updateData = {
        category_id: selectedCategory.category_id,
        ...formData
      }

      const response = await fetch(`http://127.0.0.1:8000/api/items/categories/${selectedCategory.category_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(updateData)
      })

      if (response.ok) {
        toast.success('Category updated successfully!')
        setShowEditModal(false)
        resetForm()
        setSelectedCategory(null)
        fetchCategories(), e) => {
    e?.stopPropagation()
    
    if (!window.confirm(`Are you sure you want to delete "${category.category_name}"?`)) {
      return
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/items/categories/${category.category_id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      })

      if (response.ok) {
        toast.success('Category deleted successfully!')
        if (selectedCategory?.category_id === category.category_id) {
          resetForm()
        }
        fetchCategories()
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to delete category')
      }
    } catch (error) {
      toast.error('Error deleting category')
      console.error(error)
    }
  }

  // Build hierarchical tree structure
  const buildTree = () => {
    const categoryMap = {}
    const tree = []

    // Create map of all categories
    categories.forEach(cat => {
      categoryMap[cat.category_id] = { ...cat, children: [] }
    })

    // Build tree structure
    categories.forEach(cat => {
      if (cat.parent_category_id && categoryMap[cat.parent_category_id]) {
        categoryMap[cat.parent_category_id].children.push(categoryMap[cat.category_id])
      } else {
        tree.push(categoryMap[cat.category_id])
      }
    })

    return tree
  }

  const filterCategories = (tree) => {
    if (!searchTerm && filterStatus === 'all' && filterClass === 'all') return tree

    const filterNode = (node) => {
      const matchesSearch = !searchTerm || 
        node.category_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.category_code.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesStatus = filterStatus === 'all' || 
        (filterStatus === 'active' && node.is_active !== false) ||
        (filterStatus === 'inactive' && node.is_active === false)
      
      const matchesClass = filterClass === 'all' || node.inventory_class === filterClass

      const filteredChildren = node.children.map(filterNode).filter(Boolean)

      if (matchesSearch && matchesStatus && matchesClass) {
        return { ...node, children: filteredChildren }
      } else if (filteredChildren.length > 0) {
        return { ...node, children: filteredChildren }
      }

      return null
    }

    return tree.map(filterNode).filter(Boolean)
  }

  const renderTreeNode = (node, level = 0) => {
    const hasChildren = node.children && node.children.length > 0
    const isExpanded = expandedNodes.has(node.category_id)
    const isSelected = selectedCategory?.category_id === node.category_id
    const isInactive = node.is_active === false

    return (
      <div key={node.category_id}>
        <div
          className={`flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-green-50 transition ${
            isSelected ? 'bg-green-100 border-l-4 border-green-600' : ''
          } ${isInactive ? 'opacity-50' : ''}`}
          style={{ paddingLeft: `${level * 20 + 12}px` }}
          onClick={() => handleEditCategory(node)}
        >
          {hasChildren ? (
            <button
              onClick={(e) => {
                e.stopPropagation()
                toggleNode(node.category_id)
              }}
              className="p-0.5 hover:bg-green-200 rounded"
            >
              {isExpanded ? (
                <ChevronDown size={16} className="text-gray-600" />
              ) : (
                <ChevronRight size={16} className="text-gray-600" />
              )}
            </button>
          ) : (
            <span className="w-5"></span>
          )}
          
          {hasChildren ? (
            isExpanded ? <FolderOpen size={16} className="text-green-600" /> : <Folder size={16} className="text-green-600" />
          ) : (
            <div className="w-4 h-4 rounded-full bg-green-200 flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
            </div>
          )}

          <div className="flex-1 min-w-0">
            <div className="font-medium text-sm text-gray-900 truncate">{node.category_name}</div>
            <div className="text-xs text-gray-500 font-mono">{node.category_code}</div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={(e) => {
                e.stopPropagation()
                handleAddChildCategory(node)
              }}
              className="p-1 hover:bg-green-200 rounded text-green-600"
              title="Add Child"
            >
              <Plus size={14} />
            </button>
            <button
              onClick={(e) => handleDeleteCategory(node, e)}
              className="p-1 hover:bg-red-100 rounded text-red-600"
              title="Delete"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {hasChildren && isExpanded && (
          <div>
            {node.children.map(child => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    ) cat.level === 2
    if (activeTab === 'level3') return matchesSearch && cat.level === 3
    return matchesSearch
  })

  const getLevelBadge = (level) => {
    const badges = {
      1: 'bg-purple-100 text-purple-700',
      2: 'bg-blue-100 text-blue-700',
      3: 'bg-green-100 text-green-700',
    }
    return badges[level] || 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="flex flex-col h-full">
      {/* Sticky Top Bar */}
      <div className="bg-white p-4 border-b flex flex-wrap items-center justify-between gap-4 sticky top-0 z-10">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search categories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        {/* Actions */}
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition shadow-sm"
        >
          <Plus size={20} />
          Add Category
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Tabs */}
        <div className="flex gap-2 mb-4 border-b">
          {[
            { key: 'all', label: 'All Categories', icon: Package },
            { key: 'level1', label: 'Level 1 - Inventory Class', icon: Package },
            { key: 'level2', label: 'Level 2 - Material Type', icon: Settings },
            { key: 'level3', label: 'Level 3 - Sub-Category', icon: ChevronRight },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key)
                handleTabPreview(tab.key)
              }}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 transition cursor-pointer hover:bg-green-50 ${
                activeTab === tab.key
                  ? 'border-green-600 text-green-600 font-medium'
                  : 'border-transparent text-gray-600 hover:text-green-600'
              }`}
              title={`Click to preview ${tab.label.toLowerCase()}`}
            >
              <tab.icon size={18} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Categories Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {loading ? (
              <div className="p-8 text-center text-gray-500">Loading categories...</div>
            ) : filteredCategories.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <p>No categories found</p>
                <p className="text-sm mt-2">Create your first category to get started</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Level</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Code</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Class</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Parent</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">UOM</th>
                      <th className="px-6 py-3 text-center text-sm font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCategories.map((category, idx) => (
                      <tr key={idx} className="border-b hover:bg-gray-50 transition">
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getLevelBadge(category.level)}`}>
                            L{category.level}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="font-mono text-sm bg-green-50 px-3 py-1 rounded text-green-700">
                            {category.category_code}
                          </span>
                        </td>
                        <td className="px-6 py-4 font-medium text-gray-900">{category.category_name}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {category.inventory_class ? (
                            <span className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs">
                              {category.inventory_class.replace('_', ' ')}
                            </span>
                          ) : '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{category.parent_category_name || '-'}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{category.default_uom?.toUpperCase() || '-'}</td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button 
                              onClick={() => handleViewCategory(category)}
                              className="p-2 hover:bg-blue-100 rounded text-blue-600 transition" 
                              title="View"
                            >
                              <Eye size={16} />
                            </button>
                            <button 
                              onClick={() => handleEditCategory(category)}
                              className="p-2 hover:bg-orange-100 rounded text-orange-600 transition" 
                              title="Edit"
                            >
                              <Edit2 size={16} />
                            </button>
                            <button 
                              onClick={() => handleDeleteCategory(category)}
                              className="p-2 hover:bg-red-100 rounded text-red-600 transition" 
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

          {/* Summary */}
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
              <p className="text-gray-600 text-sm">Level 1</p>
              <p className="text-2xl font-bold text-purple-600">{categories.filter(c => c.level === 1).length}</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-gray-600 text-sm">Level 2</p>
              <p className="text-2xl font-bold text-blue-600">{categories.filter(c => c.level === 2).length}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <p className="text-gray-600 text-sm">Level 3</p>
              <p className="text-2xl font-bold text-green-600">{categories.filter(c => c.level === 3).length}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-gray-600 text-sm">Total</p>
              <p className="text-2xl font-bold text-gray-600">{filteredCategories.length}</p>
            </div>
          </div>
        </div>

      {/* Add Modal */}
      {showAddModal && (
        <Modal title="Add New Category" onClose={() => { setShowAddModal(false); resetForm(); }}>
          <CategoryForm 
            formData={formData}
            setFormData={setFormData}
            onSubmit={handleAddCategory}
            inventoryClasses={inventoryClasses}
            unitsOfMeasure={unitsOfMeasure}
            categories={categories}
            isEditing={false}
          />
        </Modal>
      )}

      {/* Edit Modal */}
      {showEditModal && (
        <Modal title="Edit Category" onClose={() => { setShowEditModal(false); resetForm(); setSelectedCategory(null); }}>
          <CategoryForm 
            formData={formData}
            setFormData={setFormData}
            onSubmit={handleUpdateCategory}
            inventoryClasses={inventoryClasses}
            unitsOfMeasure={unitsOfMeasure}
            categories={categories}
            isEditing={true}
          />
        </Modal>
      )}

      {/* View Modal */}
      {showViewModal && selectedCategory && (
        <Modal title="View Category Details" onClose={() => { setShowViewModal(false); setSelectedCategory(null); }}>
          <CategoryView category={selectedCategory} />
        </Modal>
      )}
    </div>
  )
}

// Modal Component
function Modal({ title, children, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-green-600 text-white p-4 flex justify-between items-center">
          <h3 className="text-xl font-semibold">{title}</h3>
          <button onClick={onClose} className="text-white hover:bg-green-700 rounded-full p-2">
            ✕
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  )
}

// Category Form Component
function CategoryForm({ formData, setFormData, onSubmit, inventoryClasses, unitsOfMeasure, categories, isEditing }) {
  const [activeFormTab, setActiveFormTab] = useState('basic')

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleParentChange = (e) => {
    const parentId = e.target.value
    const parent = categories.find(c => c.category_id === parentId)
    setFormData(prev => ({
      ...prev,
      parent_category_id: parentId || null,
      parent_category_name: parent?.category_name || null,
      level: parentId ? (parent.level + 1) : 1
    }))
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex gap-2 border-b">
        {[
          { key: 'basic', label: 'Basic Info' },
          { key: 'inventory', label: 'Inventory Details' },
          { key: 'cost', label: 'Cost & Supplier' },
          { key: 'quality', label: 'Quality & Storage' },
        ].map(tab => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveFormTab(tab.key)}
            className={`px-4 py-2 border-b-2 transition ${
              activeFormTab === tab.key
                ? 'border-green-600 text-green-600 font-medium'
                : 'border-transparent text-gray-600 hover:text-green-600'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Basic Info Tab */}
      {activeFormTab === 'basic' && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category Code *</label>
            <input
              type="text"
              name="category_code"
              value={formData.category_code}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              required
              disabled={isEditing}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category Name *</label>
            <input
              type="text"
              name="category_name"
              value={formData.category_name}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Parent Category</label>
            <select
              name="parent_category_id"
              value={formData.parent_category_id || ''}
              onChange={handleParentChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">-- None (Level 1) --</option>
              {categories.filter(c => c.level < 3).map(cat => (
                <option key={cat.category_id} value={cat.category_id}>
                  L{cat.level}: {cat.category_name} ({cat.category_code})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Level (Auto)</label>
            <input
              type="number"
              value={formData.level}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100"
              disabled
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort Order</label>
            <input
              type="number"
              name="sort_order"
              value={formData.sort_order}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>
      )}

      {/* Inventory Details Tab */}
      {activeFormTab === 'inventory' && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Inventory Class</label>
            <select
              name="inventory_class"
              value={formData.inventory_class || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">-- Select Class --</option>
              {inventoryClasses.map(cls => (
                <option key={cls} value={cls}>{cls.replace('_', ' ')}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Default Unit of Measure</label>
            <select
              name="default_uom"
              value={formData.default_uom || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">-- Select UOM --</option>
              {unitsOfMeasure.map(uom => (
                <option key={uom} value={uom}>{uom.toUpperCase()}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Waste Percentage (%)</label>
            <input
              type="number"
              name="waste_percentage"
              value={formData.waste_percentage}
              onChange={handleChange}
              step="0.1"
              min="0"
              max="100"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Reorder Point</label>
            <input
              type="number"
              name="reorder_point"
              value={formData.reorder_point || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Lead Time (Days)</label>
            <input
              type="number"
              name="lead_time_days"
              value={formData.lead_time_days || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div className="col-span-2">
            <div className="flex gap-6">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  name="requires_batch_tracking"
                  checked={formData.requires_batch_tracking}
                  onChange={handleChange}
                  className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
                />
                <span className="text-sm text-gray-700">Requires Batch Tracking</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  name="requires_expiry_tracking"
                  checked={formData.requires_expiry_tracking}
                  onChange={handleChange}
                  className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
                />
                <span className="text-sm text-gray-700">Requires Expiry Tracking</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  name="quality_check_required"
                  checked={formData.quality_check_required}
                  onChange={handleChange}
                  className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
                />
                <span className="text-sm text-gray-700">Quality Check Required</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Cost & Supplier Tab */}
      {activeFormTab === 'cost' && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Standard Cost</label>
            <input
              type="number"
              name="standard_cost"
              value={formData.standard_cost || ''}
              onChange={handleChange}
              step="0.01"
              min="0"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Supplier ID</label>
            <input
              type="text"
              name="preferred_supplier_id"
              value={formData.preferred_supplier_id || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Supplier Name</label>
            <input
              type="text"
              name="preferred_supplier_name"
              value={formData.preferred_supplier_name}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>
      )}

      {/* Quality & Storage Tab */}
      {activeFormTab === 'quality' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Storage Requirements</label>
            <textarea
              name="storage_requirements"
              value={formData.storage_requirements}
              onChange={handleChange}
              rows="4"
              placeholder="e.g., Store in cool, dry place away from direct sunlight"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Handling Instructions</label>
            <textarea
              name="handling_instructions"
              value={formData.handling_instructions}
              onChange={handleChange}
              rows="4"
              placeholder="e.g., Handle with care, avoid folding"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={() => { setFormData(formData); }}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
        >
          {isEditing ? 'Update' : 'Create'} Category
        </button>
      </div>
    </form>
  )
}

// Category View Component
function CategoryView({ category }) {
  return (
    <div className="space-y-6">
      {/* Basic Info */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-3 pb-2 border-b">Basic Information</h4>
        <div className="grid grid-cols-2 gap-4">
          <InfoField label="Category Code" value={category.category_code} />
          <InfoField label="Category Name" value={category.category_name} />
          <InfoField label="Level" value={`Level ${category.level}`} />
          <InfoField label="Parent Category" value={category.parent_category_name || 'None'} />
          <InfoField label="Description" value={category.description || '-'} className="col-span-2" />
        </div>
      </div>

      {/* Inventory Details */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-3 pb-2 border-b">Inventory Details</h4>
        <div className="grid grid-cols-2 gap-4">
          <InfoField label="Inventory Class" value={category.inventory_class?.replace('_', ' ') || '-'} />
          <InfoField label="Unit of Measure" value={category.default_uom?.toUpperCase() || '-'} />
          <InfoField label="Waste Percentage" value={category.waste_percentage ? `${category.waste_percentage}%` : '-'} />
          <InfoField label="Reorder Point" value={category.reorder_point || '-'} />
          <InfoField label="Lead Time" value={category.lead_time_days ? `${category.lead_time_days} days` : '-'} />
          <div className="col-span-2 flex gap-6">
            <InfoField label="Batch Tracking" value={category.requires_batch_tracking ? '✓ Yes' : '✗ No'} />
            <InfoField label="Expiry Tracking" value={category.requires_expiry_tracking ? '✓ Yes' : '✗ No'} />
            <InfoField label="Quality Check" value={category.quality_check_required ? '✓ Yes' : '✗ No'} />
          </div>
        </div>
      </div>

      {/* Cost & Supplier */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-3 pb-2 border-b">Cost & Supplier</h4>
        <div className="grid grid-cols-2 gap-4">
          <InfoField label="Standard Cost" value={category.standard_cost ? `₹${category.standard_cost}` : '-'} />
          <InfoField label="Supplier ID" value={category.preferred_supplier_id || '-'} />
          <InfoField label="Supplier Name" value={category.preferred_supplier_name || '-'} className="col-span-2" />
        </div>
      </div>

      {/* Storage & Handling */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-3 pb-2 border-b">Storage & Handling</h4>
        <div className="space-y-3">
          <InfoField label="Storage Requirements" value={category.storage_requirements || '-'} />
          <InfoField label="Handling Instructions" value={category.handling_instructions || '-'} />
        </div>
      </div>

      {/* Tab Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col">
            {/* Preview Header */}
            <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-green-600 to-green-800 text-white rounded-t-lg">
              <div className="flex items-center gap-3">
                {previewType === 'all' && <Package size={24} />}
                {previewType === 'level1' && <Package size={24} />}
                {previewType === 'level2' && <Settings size={24} />}
                {previewType === 'level3' && <ChevronRight size={24} />}
                <h3 className="text-xl font-bold">
                  {previewType === 'all' && 'All Categories Preview'}
                  {previewType === 'level1' && 'Level 1 - Inventory Class Preview'}
                  {previewType === 'level2' && 'Level 2 - Material Type Preview'}
                  {previewType === 'level3' && 'Level 3 - Sub-Category Preview'}
                </h3>
              </div>
              <button
                onClick={closePreview}
                className="p-2 hover:bg-white/20 rounded-lg transition"
              >
                <X size={24} />
              </button>
            </div>

            {/* Preview Content */}
            <div className="flex-1 p-6 overflow-auto">
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold text-green-800 mb-2">
                    {previewType === 'all' && 'Complete Category Overview'}
                    {previewType === 'level1' && 'Level 1 Categories - Inventory Classes'}
                    {previewType === 'level2' && 'Level 2 Categories - Material Types'}
                    {previewType === 'level3' && 'Level 3 Categories - Sub-Categories'}
                  </h4>
                  <p className="text-green-700 text-sm">
                    Total Items: {previewData?.length || 0} | 
                    Enhanced category management for manufacturing
                  </p>
                </div>
                
                {previewData && previewData.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {previewData.slice(0, 12).map((item, index) => (
                      <div key={index} className="bg-white border rounded-lg p-4 shadow-sm hover:shadow-md transition">
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0">
                            {previewType === 'level1' && <Package size={16} className="text-green-600 mt-1" />}
                            {previewType === 'level2' && <Settings size={16} className="text-blue-600 mt-1" />}
                            {previewType === 'level3' && <ChevronRight size={16} className="text-purple-600 mt-1" />}
                            {previewType === 'all' && <Eye size={16} className="text-gray-600 mt-1" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <h5 className="font-medium text-gray-900 truncate">{item.category_name}</h5>
                            <p className="text-sm text-gray-600 font-mono">{item.category_code}</p>
                            <p className="text-xs text-gray-500">Level {item.level}</p>
                            
                            <div className="mt-2 space-y-1">
                              {item.inventory_class && (
                                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-2">
                                  {item.inventory_class.replace('_', ' ')}
                                </span>
                              )}
                              {item.default_uom && (
                                <span className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded mr-2">
                                  {item.default_uom.toUpperCase()}
                                </span>
                              )}
                              {item.requires_batch_tracking && (
                                <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded mr-2">
                                  Batch Tracking
                                </span>
                              )}
                              {item.quality_check_required && (
                                <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                                  Quality Check
                                </span>
                              )}
                            </div>
                            
                            {item.description && (
                              <p className="text-xs text-gray-400 mt-2 line-clamp-2">{item.description}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                    {previewData.length > 12 && (
                      <div className="col-span-full text-center py-4 text-gray-500">
                        ... and {previewData.length - 12} more categories
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Package size={48} className="mx-auto mb-4 text-gray-300" />
                    <p>No categories available for this level</p>
                  </div>
                )}
              </div>
            </div>

            {/* Preview Footer */}
            <div className="border-t p-4 bg-gray-50 rounded-b-lg">
              <div className="flex justify-between items-center">
                <p className="text-sm text-gray-600">
                  Preview generated at {new Date().toLocaleTimeString()}
                </p>
                <button
                  onClick={closePreview}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition"
                >
                  Close Preview
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function InfoField({ label, value, className = '' }) {
  return (
    <div className={className}>
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className="text-gray-900 font-medium">{value}</p>
    </div>
  )
}
