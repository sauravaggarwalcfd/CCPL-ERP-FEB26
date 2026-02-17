import { useState, useEffect } from 'react'
import { Plus, ChevronRight, ChevronDown, Trash2, FolderTree, FolderOpen, Folder, AlertTriangle, Trash, RefreshCw, X, Edit } from 'lucide-react'
import toast from 'react-hot-toast'
import { useLayout } from '../context/LayoutContext'
import { categoryHierarchy } from '../services/api'

const LEVEL_CONFIG = {
  1: { name: 'Category', color: 'green', apiKey: 'categories' },
  2: { name: 'Sub-Category', color: 'blue', apiKey: 'sub-categories' },
  3: { name: 'Division', color: 'purple', apiKey: 'divisions' },
  4: { name: 'Class', color: 'pink', apiKey: 'classes' },
  5: { name: 'Sub-Class', color: 'yellow', apiKey: 'sub-classes' },
}

const ICONS = ['Package', 'Box', 'Layers', 'Tag', 'Hash', 'Circle', 'Square', 'Star', 'Heart', 'Shield']

export default function ItemCategoryHierarchy() {
  const { setTitle } = useLayout()
  const [tree, setTree] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedNodes, setExpandedNodes] = useState(new Set())
  const [selectedNode, setSelectedNode] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [modalMode, setModalMode] = useState('create') // 'create' or 'edit'
  const [parentNode, setParentNode] = useState(null)

  // Bin functionality
  const [showBinModal, setShowBinModal] = useState(false)
  const [binItems, setBinItems] = useState([])
  const [loadingBin, setLoadingBin] = useState(false)

  // Delete confirmation
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleteConfirmText, setDeleteConfirmText] = useState('')

  // Form data
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    icon: 'Package',
    color_code: '#10b981',
    sort_order: 0,
    hsn_code: '',
    gst_rate: 0,
  })

  useEffect(() => {
    setTitle('Category Hierarchy')
    fetchTree()
  }, [setTitle])

  const fetchTree = async () => {
    try {
      setLoading(true)
      const response = await categoryHierarchy.getTree(true)
      setTree(response.data || [])
    } catch (error) {
      toast.error('Failed to fetch hierarchy tree')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      code: '',
      name: '',
      description: '',
      icon: 'Package',
      color_code: '#10b981',
      sort_order: 0,
      hsn_code: '',
      gst_rate: 0,
    })
    setParentNode(null)
    setSelectedNode(null)
    setModalMode('create')
  }

  const handleAddRoot = () => {
    resetForm()
    setModalMode('create')
    setParentNode(null)
    setShowModal(true)
  }

  const handleAddChild = (node) => {
    if (node.level >= 5) {
      toast.error('Cannot add children beyond level 5')
      return
    }

    resetForm()
    setModalMode('create')
    setParentNode(node)
    setFormData(prev => ({
      ...prev,
      color_code: node.color_code || '#10b981',
      icon: node.icon || 'Package'
    }))
    setShowModal(true)
  }

  const handleEdit = (node) => {
    setSelectedNode(node)
    setModalMode('edit')
    setFormData({
      code: node.code,
      name: node.name,
      description: node.description || '',
      icon: node.icon || 'Package',
      color_code: node.color_code || '#10b981',
      sort_order: node.sort_order || 0,
      hsn_code: node.hsn_code || '',
      gst_rate: node.gst_rate || 0,
    })
    setShowModal(true)
  }

  const getApiEndpoint = (level, parentNode = null) => {
    const config = LEVEL_CONFIG[level]
    if (!config) return null

    const data = {
      [`${getCodeField(level)}`]: formData.code.toUpperCase(),
      [`${getNameField(level)}`]: formData.name,
      description: formData.description,
      icon: formData.icon,
      color_code: formData.color_code,
      sort_order: formData.sort_order,
    }

    // Add HSN/GST for levels 4 and 5
    if (level >= 4) {
      data.hsn_code = formData.hsn_code || null
      data.gst_rate = formData.gst_rate || null
    }

    // Add parent references
    if (parentNode) {
      if (parentNode.level === 1) {
        data.category_code = parentNode.code
      } else if (parentNode.level === 2) {
        const parts = parentNode.path.split('/')
        data.category_code = parts[0]
        data.sub_category_code = parentNode.code
      } else if (parentNode.level === 3) {
        const parts = parentNode.path.split('/')
        data.category_code = parts[0]
        data.sub_category_code = parts[1]
        data.division_code = parentNode.code
      } else if (parentNode.level === 4) {
        const parts = parentNode.path.split('/')
        data.category_code = parts[0]
        data.sub_category_code = parts[1]
        data.division_code = parts[2]
        data.class_code = parentNode.code
      }
    }

    return { apiKey: config.apiKey, data }
  }

  const getCodeField = (level) => {
    const fields = ['category_code', 'sub_category_code', 'division_code', 'class_code', 'sub_class_code']
    return fields[level - 1]
  }

  const getNameField = (level) => {
    const fields = ['category_name', 'sub_category_name', 'division_name', 'class_name', 'sub_class_name']
    return fields[level - 1]
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.code || !formData.name) {
      toast.error('Code and Name are required')
      return
    }

    if (!/^[A-Z0-9]{2,4}$/.test(formData.code.toUpperCase())) {
      toast.error('Code must be 2-4 alphanumeric characters')
      return
    }

    try {
      const targetLevel = modalMode === 'create' ? (parentNode ? parentNode.level + 1 : 1) : selectedNode.level
      const { apiKey, data } = getApiEndpoint(targetLevel, parentNode)

      if (modalMode === 'create') {
        await categoryHierarchy.create(apiKey, data)
        toast.success(`${LEVEL_CONFIG[targetLevel].name} created successfully`)
      } else {
        await categoryHierarchy.update(apiKey, selectedNode.code, data)
        toast.success(`${LEVEL_CONFIG[targetLevel].name} updated successfully`)
      }

      setShowModal(false)
      resetForm()
      fetchTree()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed')
      console.error(error)
    }
  }

  const handleDelete = (node) => {
    setDeleteTarget(node)
    setDeleteConfirmText('')
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (!deleteTarget) return

    const hasChildren = deleteTarget.child_count > 0
    if (hasChildren && deleteConfirmText !== 'DELETE') {
      toast.error('You must type "DELETE" to confirm cascade deletion')
      return
    }

    try {
      const apiKey = LEVEL_CONFIG[deleteTarget.level].apiKey

      await categoryHierarchy.delete(apiKey, deleteTarget.code, hasChildren ? { force: true } : {})
      toast.success(`Deleted successfully${hasChildren ? ` (${deleteTarget.child_count} children also deleted)` : ''}`)

      setShowDeleteModal(false)
      setDeleteTarget(null)
      setDeleteConfirmText('')
      fetchTree()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Delete failed')
    }
  }

  // Bin management
  const handleOpenBin = async () => {
    setLoadingBin(true)
    setShowBinModal(true)
    try {
      const response = await fetch('http://127.0.0.1:8000/api/hierarchy/bin', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      })
      const data = await response.json()
      setBinItems(data || [])
    } catch (error) {
      toast.error('Failed to fetch bin items')
      setBinItems([])
    } finally {
      setLoadingBin(false)
    }
  }

  const handleRestoreFromBin = async (item) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/hierarchy/bin/restore/${item.type}/${item.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      })

      if (response.ok) {
        toast.success('Item restored successfully')
        handleOpenBin()
        fetchTree()
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to restore item')
      }
    } catch (error) {
      toast.error('Error restoring item')
    }
  }

  const handlePermanentDelete = async (item) => {
    if (!window.confirm(`⚠️ Permanently delete "${item.name}"? This cannot be undone!`)) return

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/hierarchy/bin/permanent/${item.type}/${item.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      })

      if (response.ok) {
        toast.success('Permanently deleted')
        handleOpenBin()
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to delete item')
      }
    } catch (error) {
      toast.error('Error deleting item')
    }
  }

  const toggleNode = (code) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(code)) {
      newExpanded.delete(code)
    } else {
      newExpanded.add(code)
    }
    setExpandedNodes(newExpanded)
  }

  const filterTree = (nodes) => {
    if (!searchTerm) return nodes

    const filterNode = (node) => {
      const matches = node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                     node.code.toLowerCase().includes(searchTerm.toLowerCase())
      const filteredChildren = node.children.map(filterNode).filter(Boolean)

      if (matches || filteredChildren.length > 0) {
        return { ...node, children: filteredChildren }
      }
      return null
    }

    return nodes.map(filterNode).filter(Boolean)
  }

  const renderTreeNode = (node, depth = 0) => {
    const hasChildren = node.children && node.children.length > 0
    const isExpanded = expandedNodes.has(node.code)
    const levelColor = LEVEL_CONFIG[node.level]?.color || 'gray'

    return (
      <div key={node.code}>
        <div
          className={`group flex items-center gap-2 px-3 py-2 hover:bg-${levelColor}-50 cursor-pointer transition-all`}
          style={{ paddingLeft: `${depth * 20 + 12}px` }}
        >
          <button
            onClick={() => hasChildren && toggleNode(node.code)}
            className="p-0.5 hover:bg-gray-200 rounded"
          >
            {hasChildren ? (
              isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
            ) : <span className="w-4"></span>}
          </button>

          {hasChildren ? (
            isExpanded ? <FolderOpen size={16} className={`text-${levelColor}-600`} /> :
            <Folder size={16} className={`text-${levelColor}-600`} />
          ) : (
            <div className={`w-4 h-4 rounded-full bg-${levelColor}-200 flex items-center justify-center`}>
              <div className={`w-2 h-2 rounded-full bg-${levelColor}-500`}></div>
            </div>
          )}

          <div className="flex-1 min-w-0" onClick={() => handleEdit(node)}>
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">{node.name}</span>
              <span className="text-xs font-mono text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                {node.code}
              </span>
              <span className={`text-xs bg-${levelColor}-100 text-${levelColor}-700 px-1.5 py-0.5 rounded`}>
                L{node.level}
              </span>
              {hasChildren && (
                <span className="text-xs bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">
                  {node.children.length}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
            {node.level < 5 && (
              <button
                onClick={(e) => { e.stopPropagation(); handleAddChild(node); }}
                className={`p-1 hover:bg-${levelColor}-200 rounded text-${levelColor}-600`}
                title="Add Child"
              >
                <Plus size={14} />
              </button>
            )}
            <button
              onClick={(e) => { e.stopPropagation(); handleEdit(node); }}
              className="p-1 hover:bg-blue-100 rounded text-blue-600"
              title="Edit"
            >
              <Edit size={14} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); handleDelete(node); }}
              className="p-1 hover:bg-red-100 rounded text-red-600"
              title="Delete"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {hasChildren && isExpanded && (
          <div>
            {node.children.map(child => renderTreeNode(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  const filteredTree = filterTree(tree)

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
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={handleAddRoot}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition shadow-sm"
          >
            <Plus size={20} />
            New Category
          </button>
          <button
            onClick={handleOpenBin}
            className="bg-red-100 text-red-700 hover:bg-red-200 px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition"
          >
            <Trash size={20} />
            Bin
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-white p-6">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading hierarchy...</div>
        ) : filteredTree.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <FolderTree size={48} className="mx-auto mb-3 text-gray-300" />
            <p className="font-medium">No categories found</p>
            <p className="text-sm mt-1">Create your first category to get started</p>
          </div>
        ) : (
          <div className="py-2">
            {filteredTree.map(node => renderTreeNode(node))}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold">
                {modalMode === 'create' ? 'Create' : 'Edit'} {
                  parentNode
                    ? LEVEL_CONFIG[parentNode.level + 1]?.name
                    : selectedNode
                      ? LEVEL_CONFIG[selectedNode.level]?.name
                      : 'Category'
                }
              </h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>

            {parentNode && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <span className="font-semibold">Parent:</span> {parentNode.name} ({parentNode.code})
                  <span className="ml-2 text-xs bg-blue-200 px-2 py-1 rounded">
                    Creating Level {parentNode.level + 1}
                  </span>
                </p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Code (2-4 chars) *</label>
                  <input
                    type="text"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                    disabled={modalMode === 'edit'}
                    maxLength={4}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100 uppercase"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  rows="2"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Icon</label>
                  <select
                    value={formData.icon}
                    onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    {ICONS.map(icon => <option key={icon} value={icon}>{icon}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Color</label>
                  <input
                    type="color"
                    value={formData.color_code}
                    onChange={(e) => setFormData({ ...formData, color_code: e.target.value })}
                    className="w-full h-10 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Sort Order</label>
                  <input
                    type="number"
                    value={formData.sort_order}
                    onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>

              {(parentNode?.level >= 3 || selectedNode?.level >= 4) && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">HSN Code</label>
                    <input
                      type="text"
                      value={formData.hsn_code}
                      onChange={(e) => setFormData({ ...formData, hsn_code: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">GST Rate (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.gst_rate}
                      onChange={(e) => setFormData({ ...formData, gst_rate: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4 border-t">
                <button
                  type="submit"
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium"
                >
                  {modalMode === 'create' ? 'Create' : 'Update'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="text-red-500" size={24} />
              <h3 className="text-lg font-bold">Confirm Deletion</h3>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Are you sure you want to delete <span className="font-medium">"{deleteTarget.name}"</span>?
            </p>

            {deleteTarget.child_count > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="text-red-500 flex-shrink-0" size={16} />
                  <div>
                    <p className="text-sm font-medium text-red-800">⚠️ Cascade Deletion Warning</p>
                    <p className="text-xs text-red-700 mt-1">
                      This has <strong>{deleteTarget.child_count} children</strong>. All will be deleted!
                    </p>
                    <div className="mt-2">
                      <label className="block text-xs font-medium text-red-800 mb-1">
                        Type "DELETE" to confirm:
                      </label>
                      <input
                        type="text"
                        value={deleteConfirmText}
                        onChange={(e) => setDeleteConfirmText(e.target.value)}
                        placeholder="Type DELETE to confirm"
                        className="w-full px-2 py-1 text-sm border border-red-300 rounded focus:outline-none focus:ring-2 focus:ring-red-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  setShowDeleteModal(false)
                  setDeleteTarget(null)
                  setDeleteConfirmText('')
                }}
                className="px-4 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                disabled={deleteTarget.child_count > 0 && deleteConfirmText !== 'DELETE'}
                className="px-4 py-2 text-sm text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:bg-red-300 disabled:cursor-not-allowed"
              >
                {deleteTarget.child_count > 0 ? 'Delete All' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bin Modal */}
      {showBinModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Trash className="text-red-600" size={24} />
                <h3 className="text-lg font-bold">Category Hierarchy Bin</h3>
                <span className="text-sm text-gray-500">({binItems.length} items)</span>
              </div>
              <button onClick={() => setShowBinModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>

            {loadingBin ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto mb-2"></div>
                <p className="text-gray-500">Loading bin items...</p>
              </div>
            ) : binItems.length === 0 ? (
              <div className="text-center py-12">
                <Trash size={48} className="mx-auto mb-3 text-gray-300" />
                <p className="text-gray-500 mb-2">Bin is empty</p>
                <p className="text-sm text-gray-400">Deleted items will appear here</p>
              </div>
            ) : (
              <div className="space-y-3">
                {binItems.map((item, index) => (
                  <div key={index} className="bg-gray-50 border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-200 text-gray-700">
                            Level {item.level} - {item.type}
                          </span>
                          <span className="text-xs text-gray-500">
                            Deleted: {new Date(item.deleted_at).toLocaleString()}
                          </span>
                        </div>
                        <h4 className="font-medium text-gray-900 mb-1">
                          {item.name} <span className="text-gray-500 text-sm">({item.id})</span>
                        </h4>
                        {item.path_name && <p className="text-sm text-gray-600">{item.path_name}</p>}
                      </div>
                      <div className="flex gap-2 ml-4">
                        <button
                          onClick={() => handleRestoreFromBin(item)}
                          className="flex items-center gap-1 bg-green-100 hover:bg-green-200 text-green-700 px-3 py-1.5 rounded-md text-sm font-medium"
                        >
                          <RefreshCw size={14} /> Restore
                        </button>
                        <button
                          onClick={() => handlePermanentDelete(item)}
                          className="flex items-center gap-1 bg-red-100 hover:bg-red-200 text-red-700 px-3 py-1.5 rounded-md text-sm font-medium"
                        >
                          <Trash size={14} /> Delete Forever
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
