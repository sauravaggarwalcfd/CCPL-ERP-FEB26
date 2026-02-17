/**
 * FieldInput Component
 * Generic field renderer that supports multiple input types
 */

import { useState, useEffect } from 'react';
import { useFieldValues } from '../../hooks/useSpecifications';

const FieldInput = ({ field, value, onChange, categoryCode, error }) => {
  const {
    field_key,
    field_name,
    field_type,
    required,
    options: customOptions = [],
    placeholder,
    min_value,
    max_value,
    source
  } = field;

  // Fetch values for SELECT fields from masters
  const shouldFetchValues = field_type === 'SELECT' && source && categoryCode;
  const { options: fetchedOptions, loading } = useFieldValues(
    categoryCode,
    field_key,
    shouldFetchValues
  );

  // Determine options to use
  const options = shouldFetchValues ? fetchedOptions : customOptions;

  const handleChange = (e) => {
    const { value: newValue, type, checked } = e.target;
    const finalValue = type === 'checkbox' ? checked : newValue;
    onChange(field_key, finalValue);
  };

  const renderField = () => {
    switch (field_type) {
      case 'SELECT':
        return (
          <select
            id={field_key}
            value={value || ''}
            onChange={handleChange}
            required={required}
            disabled={loading}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">
              {loading ? 'Loading...' : `Select ${field_name}`}
            </option>
            {options.map((option) => {
              // Handle both simple string options and FieldOption objects
              const optionCode = option.code || option;
              const optionName = option.name || option;
              const additionalInfo = option.additional_info || {};

              return (
                <option key={optionCode} value={optionCode}>
                  {optionName}
                  {additionalInfo.symbol && ` (${additionalInfo.symbol})`}
                </option>
              );
            })}
          </select>
        );

      case 'TEXT':
      case 'TEXTAREA':
        const Component = field_type === 'TEXTAREA' ? 'textarea' : 'input';
        return (
          <Component
            type="text"
            id={field_key}
            value={value || ''}
            onChange={handleChange}
            required={required}
            placeholder={placeholder || `Enter ${field_name}`}
            rows={field_type === 'TEXTAREA' ? 3 : undefined}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        );

      case 'NUMBER':
        return (
          <input
            type="number"
            id={field_key}
            value={value || ''}
            onChange={handleChange}
            required={required}
            placeholder={placeholder || `Enter ${field_name}`}
            min={min_value}
            max={max_value}
            step="any"
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        );

      case 'CHECKBOX':
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              id={field_key}
              checked={!!value}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor={field_key} className="ml-2 text-sm text-gray-700">
              {field_name}
            </label>
          </div>
        );

      case 'DATE':
        return (
          <input
            type="date"
            id={field_key}
            value={value || ''}
            onChange={handleChange}
            required={required}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        );

      default:
        return (
          <input
            type="text"
            id={field_key}
            value={value || ''}
            onChange={handleChange}
            required={required}
            placeholder={placeholder || `Enter ${field_name}`}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        );
    }
  };

  // Don't render checkbox label separately
  if (field_type === 'CHECKBOX') {
    return (
      <div className="mb-4">
        {renderField()}
        {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
      </div>
    );
  }

  return (
    <div className="mb-4">
      <label
        htmlFor={field_key}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {field_name}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {renderField()}
      {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
      {placeholder && field_type !== 'TEXT' && field_type !== 'TEXTAREA' && field_type !== 'NUMBER' && (
        <p className="text-xs text-gray-500 mt-1">{placeholder}</p>
      )}
    </div>
  );
};

export default FieldInput;
