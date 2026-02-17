import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Plus, Edit2, Trash2, X, Save } from 'lucide-react';
import { variantGroupApi } from '../../services/variantApi';

const VariantGroupManager = ({ variantType, onClose }) => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingGroup, setEditingGroup] = useState(null);
  const [formData, setFormData] = useState({
    group_code: '',
    group_name: '',
    description: '',
    display_order: 0
  });

  useEffect(() => {
    loadGroups();
  }, [variantType]);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const res = await variantGroupApi.getByType(variantType);
      setGroups(res.data || []);
    } catch (error) {
      console.error('Error loading groups:', error);
      toast.error('Failed to load groups');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (group) => {
    setEditingGroup(group);
    setFormData({
      group_code: group.group_code,
      group_name: group.group_name,
      description: group.description || '',
      display_order: group.display_order || 0
    });
  };

  const handleCreate = () => {
    setEditingGroup(null);
    setFormData({
      group_code: '',
      group_name: '',
      description: '',
      display_order: groups.length + 1
    });
  };

  const handleDelete = async (group) => {
    if (!confirm(`Are you sure you want to delete group "${group.group_name}"?`)) {
      return;
    }
    try {
      await variantGroupApi.delete(group.group_code);
      toast.success('Group deleted successfully');
      loadGroups();
    } catch (error) {
      console.error('Error deleting group:', error);
      toast.error('Failed to delete group');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingGroup) {
        await variantGroupApi.update(editingGroup.group_code, {
            ...formData,
            is_active: true
        });
        toast.success('Group updated successfully');
      } else {
        await variantGroupApi.create({
          ...formData,
          variant_type: variantType,
          is_active: true
        });
        toast.success('Group created successfully');
      }
      setEditingGroup(null);
      setFormData({ group_code: '', group_name: '', description: '', display_order: 0 });
      loadGroups();
    } catch (error) {
      console.error('Error saving group:', error);
      toast.error(error.response?.data?.detail || 'Failed to save group');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b flex items-center justify-between bg-gray-50 rounded-t-xl">
          <h2 className="text-xl font-bold text-gray-800">Manage {variantType} Groups</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
          {/* List Section */}
          <div className="flex-1 overflow-y-auto p-4 border-r">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-700">Existing Groups</h3>
              <button
                onClick={handleCreate}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
              >
                <Plus className="w-4 h-4" /> New Group
              </button>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : (
              <div className="space-y-2">
                {groups.map(group => (
                  <div 
                    key={group.group_code}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      editingGroup?.group_code === group.group_code 
                        ? 'bg-blue-50 border-blue-200' 
                        : 'hover:bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div onClick={() => handleEdit(group)} className="flex-1">
                        <div className="font-medium text-gray-900">{group.group_name}</div>
                        <div className="text-xs text-gray-500">{group.group_code}</div>
                      </div>
                      <button 
                        onClick={() => handleDelete(group)}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
                {groups.length === 0 && (
                  <div className="text-center py-8 text-gray-400 text-sm">No groups found</div>
                )}
              </div>
            )}
          </div>

          {/* Form Section */}
          <div className="w-full md:w-80 p-4 bg-gray-50">
            <h3 className="font-semibold text-gray-700 mb-4">
              {editingGroup ? 'Edit Group' : 'Add New Group'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Group Code</label>
                <input
                  type="text"
                  value={formData.group_code}
                  onChange={e => setFormData({...formData, group_code: e.target.value.toUpperCase()})}
                  disabled={!!editingGroup}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  placeholder="e.g. FABRIC_COLORS"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Group Name</label>
                <input
                  type="text"
                  value={formData.group_name}
                  onChange={e => setFormData({...formData, group_name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Fabric Colors"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={e => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="3"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
                <input
                  type="number"
                  value={formData.display_order}
                  onChange={e => setFormData({...formData, display_order: parseInt(e.target.value) || 0})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="pt-2 flex gap-2">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {editingGroup ? 'Update' : 'Create'}
                </button>
                {editingGroup && (
                  <button
                    type="button"
                    onClick={handleCreate}
                    className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-600"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VariantGroupManager;
