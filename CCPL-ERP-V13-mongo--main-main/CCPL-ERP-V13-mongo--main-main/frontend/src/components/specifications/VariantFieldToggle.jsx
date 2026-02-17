/**
 * VariantFieldToggle Component
 * Toggle and configure variant fields (Colour, Size, UOM, Vendor)
 */

import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

const VariantFieldToggle = ({ field, fieldKey, config, groups, onUpdate }) => {
  const [isExpanded, setIsExpanded] = useState(config?.enabled || false);
  const [fieldConfig, setFieldConfig] = useState({
    enabled: false,
    required: false,
    groups: [],
    allow_multiple: false,
    default_value: null
  });

  useEffect(() => {
    if (config) {
      setFieldConfig({
        enabled: config.enabled || false,
        required: config.required || false,
        groups: config.groups || [],
        allow_multiple: config.allow_multiple || false,
        default_value: config.default_value || null
      });
      setIsExpanded(config.enabled || false);
    }
  }, [config]);

  const handleToggle = (e) => {
    const enabled = e.target.checked;
    const newConfig = {
      ...fieldConfig,
      enabled
    };
    setFieldConfig(newConfig);
    setIsExpanded(enabled);
    onUpdate(fieldKey, newConfig);
  };

  const handleRequiredChange = (e) => {
    const required = e.target.checked;
    const newConfig = {
      ...fieldConfig,
      required
    };
    setFieldConfig(newConfig);
    onUpdate(fieldKey, newConfig);
  };

  const handleGroupsChange = (e) => {
    const options = e.target.selectedOptions;
    const selectedGroups = Array.from(options).map(opt => opt.value);
    const newConfig = {
      ...fieldConfig,
      groups: selectedGroups
    };
    setFieldConfig(newConfig);
    onUpdate(fieldKey, newConfig);
  };

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={fieldConfig.enabled}
            onChange={handleToggle}
            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <div>
            <h4 className="font-medium text-gray-900">{field}</h4>
            <p className="text-sm text-gray-500">
              {fieldConfig.enabled ? 'Enabled' : 'Disabled'} •
              {fieldConfig.required ? ' Required' : ' Optional'}
            </p>
          </div>
        </div>

        {fieldConfig.enabled && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-gray-200 rounded transition-colors"
          >
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            )}
          </button>
        )}
      </div>

      {/* Expanded Configuration */}
      {fieldConfig.enabled && isExpanded && (
        <div className="p-4 bg-white space-y-4 border-t">
          {/* Required Toggle */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id={`${fieldKey}-required`}
              checked={fieldConfig.required}
              onChange={handleRequiredChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor={`${fieldKey}-required`} className="ml-2 text-sm text-gray-700">
              Required field
            </label>
          </div>

          {/* Groups Selection */}
          {groups && groups.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Groups
              </label>
              <select
                multiple
                value={fieldConfig.groups}
                onChange={handleGroupsChange}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                size={Math.min(groups.length, 5)}
              >
                {groups.map((group) => (
                  <option key={group.code || group.value} value={group.code || group.value}>
                    {group.name || group.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">
                Hold Ctrl/Cmd to select multiple groups. Leave empty for all.
              </p>
            </div>
          )}

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded p-3">
            <p className="text-xs text-blue-800">
              <strong>Source:</strong> {fieldKey === 'colour' ? 'Colour Master' :
                                          fieldKey === 'size' ? 'Size Master' :
                                          fieldKey === 'uom' ? 'UOM Master' :
                                          'Supplier Master'}
            </p>
            {fieldConfig.groups.length > 0 && (
              <p className="text-xs text-blue-800 mt-1">
                <strong>Filtered Groups:</strong> {fieldConfig.groups.join(', ')}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default VariantFieldToggle;
