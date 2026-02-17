/**
 * Size Form Component
 * Form for creating/editing sizes
 */

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const SizeForm = ({ size, groups, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    size_code: '',
    size_name: '',
    size_group: '',
    numeric_value: '',
    unit: 'SIZE',
    description: '',
    display_order: 0,
  });

  useEffect(() => {
    if (size) {
      setFormData({
        size_code: size.size_code || '',
        size_name: size.size_name || '',
        size_group: size.size_group || '',
        numeric_value: size.numeric_value || '',
        unit: size.unit || 'SIZE',
        description: size.description || '',
        display_order: size.display_order || 0,
      });
    }
  }, [size]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Prepare data - convert numeric_value to null if empty
    const submitData = {
      ...formData,
      numeric_value: formData.numeric_value ? parseFloat(formData.numeric_value) : null,
    };

    onSubmit(submitData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {size ? 'Edit Size' : 'Add New Size'}
          </h2>
          <button
            onClick={onCancel}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Size Code */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Size Code *
            </label>
            <input
              type="text"
              name="size_code"
              value={formData.size_code}
              onChange={handleChange}
              disabled={!!size}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              placeholder="e.g., M, 32, LG"
            />
          </div>

          {/* Size Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Size Name *
            </label>
            <input
              type="text"
              name="size_name"
              value={formData.size_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Medium, Size 32"
            />
          </div>

          {/* Size Group */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Size Group *
            </label>
            <select
              name="size_group"
              value={formData.size_group}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select Group</option>
              {groups.map((group) => (
                <option key={group.code} value={group.code}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          {/* Numeric Value (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Numeric Value (Optional)
            </label>
            <input
              type="number"
              name="numeric_value"
              value={formData.numeric_value}
              onChange={handleChange}
              step="0.01"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., 32, 34, 36"
            />
            <p className="text-xs text-gray-500 mt-1">
              For numeric sizes like 28, 30, 32, etc.
            </p>
          </div>

          {/* Unit */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Unit
            </label>
            <input
              type="text"
              name="unit"
              value={formData.unit}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., SIZE, INCHES"
            />
          </div>

          {/* Display Order */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Display Order
            </label>
            <input
              type="number"
              name="display_order"
              value={formData.display_order}
              onChange={handleChange}
              min="0"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Optional description"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {size ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SizeForm;
