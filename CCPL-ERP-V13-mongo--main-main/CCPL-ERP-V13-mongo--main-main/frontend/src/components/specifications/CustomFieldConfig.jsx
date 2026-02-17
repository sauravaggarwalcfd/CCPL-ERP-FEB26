/**
 * CustomFieldConfig Component
 * Manage custom fields for a category
 */

import { useState } from 'react';
import { Plus, Edit2, Trash2, X, GripVertical } from 'lucide-react';

const FIELD_TYPES = [
  { value: 'SELECT', label: 'Dropdown (Select)' },
  { value: 'TEXT', label: 'Text Input' },
  { value: 'NUMBER', label: 'Number Input' },
  { value: 'TEXTAREA', label: 'Text Area' },
  { value: 'CHECKBOX', label: 'Checkbox' },
  { value: 'DATE', label: 'Date Picker' }
];

const CustomFieldConfig = ({ customFields = [], onAdd, onUpdate, onDelete }) => {
  const [showForm, setShowForm] = useState(false);
  const [editingField, setEditingField] = useState(null);
  const [formData, setFormData] = useState({
    field_code: '',
    field_name: '',
    field_type: 'SELECT',
    enabled: true,
    required: false,
    options: [],
    default_value: null,
    placeholder: '',
    min_value: null,
    max_value: null,
    display_order: 0
  });
  const [optionsText, setOptionsText] = useState('');

  const handleOpenForm = (field = null) => {
    if (field) {
      setEditingField(field);
      setFormData({
        field_code: field.field_code,
        field_name: field.field_name,
        field_type: field.field_type,
        enabled: field.enabled,
        required: field.required,
        options: field.options || [],
        default_value: field.default_value,
        placeholder: field.placeholder || '',
        min_value: field.min_value,
        max_value: field.max_value,
        display_order: field.display_order || 0
      });
      setOptionsText((field.options || []).join('\n'));
    } else {
      setEditingField(null);
      setFormData({
        field_code: '',
        field_name: '',
        field_type: 'SELECT',
        enabled: true,
        required: false,
        options: [],
        default_value: null,
        placeholder: '',
        min_value: null,
        max_value: null,
        display_order: customFields.length
      });
      setOptionsText('');
    }
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingField(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Parse options from text
    const options = formData.field_type === 'SELECT'
      ? optionsText.split('\n').filter(opt => opt.trim() !== '').map(opt => opt.trim())
      : [];

    const fieldData = {
      ...formData,
      options,
      field_code: formData.field_code.toUpperCase().replace(/\s+/g, '_')
    };

    if (editingField) {
      onUpdate(editingField.field_code, fieldData);
    } else {
      onAdd(fieldData);
    }

    handleCloseForm();
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const needsOptions = formData.field_type === 'SELECT';
  const needsMinMax = formData.field_type === 'NUMBER';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-gray-900">Custom Fields</h4>
        <button
          onClick={() => handleOpenForm()}
          className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Custom Field
        </button>
      </div>

      {/* Custom Fields List */}
      {customFields.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
          <p className="text-sm text-gray-600">No custom fields configured</p>
          <p className="text-xs text-gray-500 mt-1">Click "Add Custom Field" to create one</p>
        </div>
      ) : (
        <div className="space-y-2">
          {customFields.map((field) => (
            <div
              key={field.field_code}
              className="bg-white border rounded-lg p-4 flex items-start gap-3"
            >
              {/* Drag Handle */}
              <div className="flex-shrink-0 text-gray-400 cursor-move">
                <GripVertical className="w-5 h-5" />
              </div>

              {/* Field Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h5 className="font-medium text-gray-900">{field.field_name}</h5>
                  <span className="text-xs px-2 py-0.5 bg-gray-100 rounded text-gray-700">
                    {field.field_type}
                  </span>
                  {field.required && (
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded">
                      Required
                    </span>
                  )}
                  {!field.enabled && (
                    <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded">
                      Disabled
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  <strong>Code:</strong> {field.field_code}
                </p>
                {field.options && field.options.length > 0 && (
                  <p className="text-sm text-gray-600 mt-1">
                    <strong>Options:</strong> {field.options.slice(0, 3).join(', ')}
                    {field.options.length > 3 && ` (+${field.options.length - 3} more)`}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleOpenForm(field)}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  title="Edit"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => onDelete(field.field_code)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b">
              <h3 className="text-xl font-semibold text-gray-900">
                {editingField ? 'Edit Custom Field' : 'Add Custom Field'}
              </h3>
              <button
                onClick={handleCloseForm}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {/* Field Code */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Field Code *
                </label>
                <input
                  type="text"
                  name="field_code"
                  value={formData.field_code}
                  onChange={handleChange}
                  disabled={!!editingField}
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                  placeholder="e.g., QUALITY_GRADE"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Unique identifier (will be converted to UPPERCASE)
                </p>
              </div>

              {/* Field Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Field Name *
                </label>
                <input
                  type="text"
                  name="field_name"
                  value={formData.field_name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Quality Grade"
                />
              </div>

              {/* Field Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Field Type *
                </label>
                <select
                  name="field_type"
                  value={formData.field_type}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {FIELD_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Options (for SELECT type) */}
              {needsOptions && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Options (one per line) *
                  </label>
                  <textarea
                    value={optionsText}
                    onChange={(e) => setOptionsText(e.target.value)}
                    required
                    rows="5"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Grade A&#10;Grade B&#10;Grade C"
                  />
                </div>
              )}

              {/* Min/Max (for NUMBER type) */}
              {needsMinMax && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Min Value
                    </label>
                    <input
                      type="number"
                      name="min_value"
                      value={formData.min_value || ''}
                      onChange={handleChange}
                      step="any"
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Value
                    </label>
                    <input
                      type="number"
                      name="max_value"
                      value={formData.max_value || ''}
                      onChange={handleChange}
                      step="any"
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              )}

              {/* Placeholder */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Placeholder
                </label>
                <input
                  type="text"
                  name="placeholder"
                  value={formData.placeholder}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Enter value"
                />
              </div>

              {/* Checkboxes */}
              <div className="flex gap-6">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="enabled"
                    name="enabled"
                    checked={formData.enabled}
                    onChange={handleChange}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="enabled" className="ml-2 text-sm text-gray-700">
                    Enabled
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="required"
                    name="required"
                    checked={formData.required}
                    onChange={handleChange}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="required" className="ml-2 text-sm text-gray-700">
                    Required
                  </label>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseForm}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {editingField ? 'Update' : 'Add'} Field
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomFieldConfig;
