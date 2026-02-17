/**
 * UOM Master Component
 * Manages UOM variants with grouping and conversion
 */

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Plus, Edit2, Trash2, Search, Calculator, Settings } from 'lucide-react';
import { uomApi } from '../../services/variantApi';
import UOMForm from './UOMForm';
import UOMConverter from './UOMConverter';
import GroupedVariantList from './GroupedVariantList';
import VariantGroupManager from './VariantGroupManager';

const UOMMaster = () => {
  const [uoms, setUoms] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [showConverter, setShowConverter] = useState(false);
  const [showGroupManager, setShowGroupManager] = useState(false);
  const [editingUOM, setEditingUOM] = useState(null);

  // Load UOMs and groups
  useEffect(() => {
    loadData();
  }, [selectedGroup]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load groups
      const groupsRes = await uomApi.getGroups();
      setGroups(groupsRes.data || []);

      // Load UOMs
      const params = {
        is_active: true,
      };
      if (selectedGroup !== 'all') {
        params.group = selectedGroup;
      }

      const uomsRes = await uomApi.list(params);
      setUoms(uomsRes.data || []);
    } catch (error) {
      console.error('Error loading UOMs:', error);
      toast.error('Failed to load UOMs');
    } finally {
      setLoading(false);
    }
  };

  // Group UOMs by uom_group
  const groupedUOMs = uoms.reduce((acc, uom) => {
    const group = uom.uom_group;
    if (!acc[group]) {
      acc[group] = [];
    }
    acc[group].push(uom);
    return acc;
  }, {});

  // Filter UOMs by search term
  const filteredGroupedUOMs = Object.keys(groupedUOMs).reduce((acc, group) => {
    const filtered = groupedUOMs[group].filter(
      (uom) =>
        uom.uom_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        uom.uom_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        uom.uom_symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
    if (filtered.length > 0) {
      acc[group] = filtered;
    }
    return acc;
  }, {});

  const handleCreate = () => {
    setEditingUOM(null);
    setShowForm(true);
  };

  const handleEdit = (uom) => {
    setEditingUOM(uom);
    setShowForm(true);
  };

  const handleDelete = async (uom) => {
    if (!confirm(`Are you sure you want to delete UOM "${uom.uom_name}"?`)) {
      return;
    }

    try {
      await uomApi.delete(uom.uom_code);
      toast.success('UOM deleted successfully');
      loadData();
    } catch (error) {
      console.error('Error deleting UOM:', error);
      let message = 'Failed to delete UOM';
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
      if (editingUOM) {
        await uomApi.update(editingUOM.uom_code, data);
        toast.success('UOM updated successfully');
      } else {
        await uomApi.create(data);
        toast.success('UOM created successfully');
      }
      setShowForm(false);
      setEditingUOM(null);
      loadData();
    } catch (error) {
      console.error('Error saving UOM:', error);
      let message = 'Failed to save UOM';
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
    setEditingUOM(null);
  };

  const renderUOMItem = (uom) => (
    <div className="flex items-center justify-between p-3 bg-white rounded-lg border hover:shadow-md transition-shadow">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900">{uom.uom_name}</span>
          <span className="text-sm px-2 py-0.5 bg-gray-100 rounded text-gray-700">
            {uom.uom_symbol}
          </span>
          {uom.is_base_uom && (
            <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
              Base
            </span>
          )}
        </div>
        <div className="text-sm text-gray-500">
          {uom.uom_code} • Conversion: {uom.conversion_to_base}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => handleEdit(uom)}
          className="p-2 text-blue-600 hover:bg-blue-50 rounded"
          title="Edit"
        >
          <Edit2 className="w-4 h-4" />
        </button>
        <button
          onClick={() => handleDelete(uom)}
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
              placeholder="Search UOMs..."
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

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowGroupManager(true)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Settings className="w-5 h-5" />
            Manage Groups
          </button>

          <button
            onClick={() => setShowConverter(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Calculator className="w-5 h-5" />
            Converter
          </button>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Add UOM
          </button>
        </div>
      </div>

      {/* Grouped List */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading UOMs...</div>
      ) : (
        <GroupedVariantList
          groupedItems={filteredGroupedUOMs}
          groups={groups}
          renderItem={renderUOMItem}
          emptyMessage="No UOMs found"
        />
      )}

      {/* Form Modal */}
      {showForm && (
        <UOMForm
          uom={editingUOM}
          groups={groups}
          onSubmit={handleFormSubmit}
          onCancel={handleFormCancel}
        />
      )}

      {/* Converter Modal */}
      {showConverter && (
        <UOMConverter uoms={uoms} onClose={() => setShowConverter(false)} />
      )}

      {/* Group Manager Modal */}
      {showGroupManager && (
        <VariantGroupManager
          variantType="UOM"
          onClose={() => {
            setShowGroupManager(false);
            loadData();
          }}
        />
      )}
    </div>
  );
};

export default UOMMaster;
