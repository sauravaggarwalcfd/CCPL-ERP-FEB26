/**
 * Size Master Component
 * Manages size variants with grouping
 */

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Plus, Edit2, Trash2, Search, Settings } from 'lucide-react';
import { sizeApi } from '../../services/variantApi';
import SizeForm from './SizeForm';
import GroupedVariantList from './GroupedVariantList';
import VariantGroupManager from './VariantGroupManager';

const SizeMaster = () => {
  const [sizes, setSizes] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [showGroupManager, setShowGroupManager] = useState(false);
  const [editingSize, setEditingSize] = useState(null);

  // Load sizes and groups
  useEffect(() => {
    loadData();
  }, [selectedGroup]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load groups
      const groupsRes = await sizeApi.getGroups();
      setGroups(groupsRes.data || []);

      // Load sizes
      const params = {
        is_active: true,
      };
      if (selectedGroup !== 'all') {
        params.group = selectedGroup;
      }

      const sizesRes = await sizeApi.list(params);
      setSizes(sizesRes.data || []);
    } catch (error) {
      console.error('Error loading sizes:', error);
      toast.error('Failed to load sizes');
    } finally {
      setLoading(false);
    }
  };

  // Group sizes by size_group
  const groupedSizes = sizes.reduce((acc, size) => {
    const group = size.size_group;
    if (!acc[group]) {
      acc[group] = [];
    }
    acc[group].push(size);
    return acc;
  }, {});

  // Filter sizes by search term
  const filteredGroupedSizes = Object.keys(groupedSizes).reduce((acc, group) => {
    const filtered = groupedSizes[group].filter(
      (size) =>
        size.size_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        size.size_code.toLowerCase().includes(searchTerm.toLowerCase())
    );
    if (filtered.length > 0) {
      acc[group] = filtered;
    }
    return acc;
  }, {});

  const handleCreate = () => {
    setEditingSize(null);
    setShowForm(true);
  };

  const handleEdit = (size) => {
    setEditingSize(size);
    setShowForm(true);
  };

  const handleDelete = async (size) => {
    if (!confirm(`Are you sure you want to delete size "${size.size_name}"?`)) {
      return;
    }

    try {
      await sizeApi.delete(size.size_code);
      toast.success('Size deleted successfully');
      loadData();
    } catch (error) {
      console.error('Error deleting size:', error);
      let message = 'Failed to delete size';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          message = error.response.data.detail.map((err) => err.msg).join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          message = error.response.data.detail;
        }
      }
      toast.error(message);
    }
  };

  const handleFormSubmit = async (data) => {
    try {
      if (editingSize) {
        await sizeApi.update(editingSize.size_code, data);
        toast.success('Size updated successfully');
      } else {
        await sizeApi.create(data);
        toast.success('Size created successfully');
      }
      setShowForm(false);
      setEditingSize(null);
      loadData();
    } catch (error) {
      console.error('Error saving size:', error);
      let message = 'Failed to save size';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          message = error.response.data.detail.map((err) => err.msg).join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          message = error.response.data.detail;
        }
      }
      toast.error(message);
    }
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingSize(null);
  };

  const renderSizeItem = (size) => (
    <div className="flex items-center justify-between p-3 bg-white rounded-lg border hover:shadow-md transition-shadow">
      <div className="flex-1">
        <div className="font-medium text-gray-900">{size.size_name}</div>
        <div className="text-sm text-gray-500">
          {size.size_code}
          {size.numeric_value && ` • ${size.numeric_value}`}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => handleEdit(size)}
          className="p-2 text-blue-600 hover:bg-blue-50 rounded"
          title="Edit"
        >
          <Edit2 className="w-4 h-4" />
        </button>
        <button
          onClick={() => handleDelete(size)}
          className="p-2 text-red-600 hover:bg-red-50 rounded"
          title="Delete"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search sizes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Group Filter */}
          <select
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Groups</option>
            {groups.map((group) => (
              <option key={group.code} value={group.code}>
                {group.name}
              </option>
            ))}
          </select>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowGroupManager(true)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Settings className="w-5 h-5" />
            Manage Groups
          </button>

          <button
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Add Size
          </button>
        </div>
      </div>

      {/* Grouped List */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading sizes...</div>
      ) : (
        <GroupedVariantList
          groupedItems={filteredGroupedSizes}
          groups={groups}
          renderItem={renderSizeItem}
          emptyMessage="No sizes found"
        />
      )}

      {/* Form Modal */}
      {showForm && (
        <SizeForm
          size={editingSize}
          groups={groups}
          onSubmit={handleFormSubmit}
          onCancel={handleFormCancel}
        />
      )}

      {/* Group Manager Modal */}
      {showGroupManager && (
        <VariantGroupManager
          variantType="SIZE"
          onClose={() => {
            setShowGroupManager(false);
            loadData();
          }}
        />
      )}
    </div>
  );
};

export default SizeMaster;
