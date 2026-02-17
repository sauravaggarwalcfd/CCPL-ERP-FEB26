/**
 * Colour Form Component
 * Form for creating/editing colours with hex picker
 */

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const ColourForm = ({ colour, groups, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    colour_code: '',
    colour_name: '',
    colour_hex: '#000000',
    colour_group: '',
    description: '',
    display_order: 0,
  });

  useEffect(() => {
    if (colour) {
      setFormData({
        colour_code: colour.colour_code || '',
        colour_name: colour.colour_name || '',
        colour_hex: colour.colour_hex || '#000000',
        colour_group: colour.colour_group || '',
        description: colour.description || '',
        display_order: colour.display_order || 0,
      });
    }
  }, [colour]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {colour ? 'Edit Colour' : 'Add New Colour'}
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
          {/* Colour Code */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Colour Code *
            </label>
            <input
              type="text"
              name="colour_code"
              value={formData.colour_code}
              onChange={handleChange}
              disabled={!!colour}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              placeholder="e.g., FAB-RED"
            />
          </div>

          {/* Colour Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Colour Name *
            </label>
            <input
              type="text"
              name="colour_name"
              value={formData.colour_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Red"
            />
          </div>

          {/* Colour Hex with Preview */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hex Colour *
            </label>
            <div className="flex gap-2">
              <input
                type="color"
                name="colour_hex"
                value={formData.colour_hex}
                onChange={handleChange}
                className="w-16 h-10 border rounded cursor-pointer"
              />
              <input
                type="text"
                name="colour_hex"
                value={formData.colour_hex}
                onChange={handleChange}
                required
                className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="#RRGGBB"
              />
            </div>
          </div>

          {/* Colour Group */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Colour Group *
            </label>
            <select
              name="colour_group"
              value={formData.colour_group}
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
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              {colour ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ColourForm;
