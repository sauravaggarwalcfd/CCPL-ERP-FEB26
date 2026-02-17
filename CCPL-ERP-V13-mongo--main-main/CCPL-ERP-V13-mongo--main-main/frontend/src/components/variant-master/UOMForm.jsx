/**
 * UOM Form Component
 * Form for creating/editing UOMs with conversion factors
 */

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const UOMForm = ({ uom, groups, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    uom_code: '',
    uom_name: '',
    uom_symbol: '',
    uom_group: '',
    conversion_to_base: 1.0,
    is_base_uom: false,
    description: '',
    display_order: 0,
  });

  useEffect(() => {
    if (uom) {
      setFormData({
        uom_code: uom.uom_code || '',
        uom_name: uom.uom_name || '',
        uom_symbol: uom.uom_symbol || '',
        uom_group: uom.uom_group || '',
        conversion_to_base: uom.conversion_to_base || 1.0,
        is_base_uom: uom.is_base_uom || false,
        description: uom.description || '',
        display_order: uom.display_order || 0,
      });
    }
  }, [uom]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Prepare data
    const submitData = {
      ...formData,
      conversion_to_base: parseFloat(formData.conversion_to_base),
    };

    onSubmit(submitData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {uom ? 'Edit UOM' : 'Add New UOM'}
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
          {/* UOM Code */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              UOM Code *
            </label>
            <input
              type="text"
              name="uom_code"
              value={formData.uom_code}
              onChange={handleChange}
              disabled={!!uom}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              placeholder="e.g., KG, M, PCS"
            />
          </div>

          {/* UOM Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              UOM Name *
            </label>
            <input
              type="text"
              name="uom_name"
              value={formData.uom_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Kilogram, Meter, Pieces"
            />
          </div>

          {/* UOM Symbol */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Symbol *
            </label>
            <input
              type="text"
              name="uom_symbol"
              value={formData.uom_symbol}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., kg, m, pcs"
            />
          </div>

          {/* UOM Group */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              UOM Group *
            </label>
            <select
              name="uom_group"
              value={formData.uom_group}
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

          {/* Conversion Factor */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Conversion to Base *
            </label>
            <input
              type="number"
              name="conversion_to_base"
              value={formData.conversion_to_base}
              onChange={handleChange}
              required
              step="0.000001"
              min="0"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Factor to convert to base unit (e.g., 1 kg = 1, 1 g = 0.001)
            </p>
          </div>

          {/* Is Base UOM */}
          <div className="flex items-center">
            <input
              type="checkbox"
              name="is_base_uom"
              id="is_base_uom"
              checked={formData.is_base_uom}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_base_uom" className="ml-2 text-sm text-gray-700">
              Is Base UOM
            </label>
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
              {uom ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UOMForm;
