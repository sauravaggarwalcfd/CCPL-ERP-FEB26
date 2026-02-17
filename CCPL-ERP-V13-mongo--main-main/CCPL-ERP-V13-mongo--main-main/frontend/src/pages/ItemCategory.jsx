import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, Eye } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ItemCategory() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState(null)

  const [formData, setFormData] = useState({
    category_name: '',
    category_code: '',
    description: '',
  })

  useEffect(() => {
    fetchCategories()
  }, [])

  const getToken = () => localStorage.getItem('access_token')

  const fetchCategories = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://127.0.0.1:8000/api/items/categories', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setCategories(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching categories:', error)
      setCategories([]) // Set empty array on error instead of showing error toast
    } finally {
      setLoading(false)
    }
  }

  const handleAddCategory = async (e) => {
    e.preventDefault()
    
    if (!formData.category_name || !formData.category_code) {
      toast.error('Category name and code are required')
      return
    }

    try {
      // Generate category_id from category_code (use uppercase code as ID)
      const categoryData = {
        category_id: formData.category_code.toUpperCase(),
        category_name: formData.category_name,
        category_code: formData.category_code,
        description: formData.description
      }

      const response = await fetch('http://127.0.0.1:8000/api/items/categories', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(categoryData)
      })

      if (response.ok) {
        toast.success('Category created successfully!')
        setShowAddModal(false)
        setFormData({ category_name: '', category_code: '', description: '' })
        fetchCategories()
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to create category')
      }
    } catch (error) {
      toast.error('Error creating category')
      console.error(error)
    }
  }

  const handleViewCategory = (category) => {
    setSelectedCategory(category)
    setShowViewModal(true)
  }

  const handleEditCategory = (category) => {
    setSelectedCategory(category)
    setFormData({
      category_name: category.category_name,
      category_code: category.category_code,
      description: category.description || '',
    })
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
        category_name: formData.category_name,
        category_code: formData.category_code,
        description: formData.description
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
        setFormData({ category_name: '', category_code: '', description: '' })
        setSelectedCategory(null)
        fetchCategories()
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to update category')
      }
    } catch (error) {
      toast.error('Error updating category')
      console.error(error)
    }
  }

  const handleDeleteCategory = async (category) => {
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

  const filteredCategories = categories.filter(cat =>
    cat.category_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cat.category_code.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="flex-1 overflow-auto">
      <div className="bg-white">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-green-600 to-green-800 text-white p-6 shadow-lg">
          <h1 className="text-3xl font-bold">Item Category</h1>
          <p className="text-green-100 mt-1">Create and manage product categories</p>
        </div>

        {/* Main Content */}
        <div className="p-6">
          {/* Filter & Add Section */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6 flex gap-4">
            <input
              type="text"
              placeholder="Search categories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg flex items-center gap-2 font-medium transition"
            >
              <Plus size={20} /> Add Category
            </button>
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
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Category Code</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Category Name</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Description</th>
                      <th className="px-6 py-3 text-center text-sm font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCategories.map((category, idx) => (
                      <tr key={idx} className="border-b hover:bg-gray-50 transition">
                        <td className="px-6 py-4">
                          <span className="font-mono text-sm bg-green-50 px-3 py-1 rounded text-green-700">
                            {category.category_code}
                          </span>
                        </td>
                        <td className="px-6 py-4 font-medium text-gray-900">{category.category_name}</td>
                        <td className="px-6 py-4 text-gray-600 text-sm">{category.description || '-'}</td>
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
          <div className="bg-green-50 rounded-lg p-4 border border-green-200 mt-6">
            <p className="text-gray-600 text-sm">Total Categories</p>
            <p className="text-2xl font-bold text-green-600 mt-2">{filteredCategories.length}</p>
          </div>
        </div>
      </div>

      {/* Add Category Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="bg-gradient-to-r from-green-600 to-green-800 text-white p-6">
              <h2 className="text-2xl font-bold">Add New Category</h2>
            </div>

            <form onSubmit={handleAddCategory} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category Code *</label>
                <input
                  type="text"
                  required
                  value={formData.category_code}
                  onChange={(e) => setFormData({...formData, category_code: e.target.value})}
                  placeholder="e.g., CLOTH, ELECTRONICS, FURNITURE"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category Name *</label>
                <input
                  type="text"
                  required
                  value={formData.category_name}
                  onChange={(e) => setFormData({...formData, category_name: e.target.value})}
                  placeholder="e.g., Clothing, Electronics, Furniture"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Enter category description..."
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div className="flex gap-3 pt-6 border-t">
                <button
                  type="submit"
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition"
                >
                  Create Category
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-6 py-2 rounded-lg font-medium transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* View Category Modal */}
      {showViewModal && selectedCategory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6">
              <h2 className="text-2xl font-bold">View Category</h2>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category Code</label>
                <div className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50">
                  {selectedCategory.category_code}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category Name</label>
                <div className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50">
                  {selectedCategory.category_name}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <div className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 min-h-20">
                  {selectedCategory.description || '(No description)'}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <div className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50">
                  {selectedCategory.is_active ? (
                    <span className="text-green-600 font-medium">Active</span>
                  ) : (
                    <span className="text-red-600 font-medium">Inactive</span>
                  )}
                </div>
              </div>

              <div className="flex gap-3 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => setShowViewModal(false)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Category Modal */}
      {showEditModal && selectedCategory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="bg-gradient-to-r from-orange-600 to-orange-800 text-white p-6">
              <h2 className="text-2xl font-bold">Edit Category</h2>
            </div>

            <form onSubmit={handleUpdateCategory} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category Code</label>
                <input
                  type="text"
                  value={formData.category_code}
                  onChange={(e) => setFormData({...formData, category_code: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category Name</label>
                <input
                  type="text"
                  value={formData.category_name}
                  onChange={(e) => setFormData({...formData, category_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              <div className="flex gap-3 pt-6 border-t">
                <button
                  type="submit"
                  className="flex-1 bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg font-medium transition"
                >
                  Update Category
                </button>
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-6 py-2 rounded-lg font-medium transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
