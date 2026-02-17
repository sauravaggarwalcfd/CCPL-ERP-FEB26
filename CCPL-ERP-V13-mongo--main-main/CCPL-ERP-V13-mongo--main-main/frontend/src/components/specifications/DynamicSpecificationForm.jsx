/**
 * DynamicSpecificationForm Component
 * Dynamically renders specification fields based on category configuration
 * Used in Item Master creation/editing
 */

import { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import FieldInput from './FieldInput';
import { useSpecifications } from '../../hooks/useSpecifications';

const DynamicSpecificationForm = ({
  categoryCode,
  initialValues = {},
  onSpecificationsChange,
  showTitle = true
}) => {
  const { specifications, formFields, loading, error } = useSpecifications(categoryCode);
  const [values, setValues] = useState({});
  const [fieldErrors, setFieldErrors] = useState({});

  // Initialize values from initialValues
  useEffect(() => {
    if (initialValues && Object.keys(initialValues).length > 0) {
      setValues(initialValues);
    }
  }, [initialValues]);

  // Update values when formFields change (category changed)
  useEffect(() => {
    if (formFields && formFields.length > 0) {
      // Clear previous values when category changes
      const newValues = {};

      // Set default values from field configuration
      formFields.forEach(field => {
        if (field.default_value !== null && field.default_value !== undefined) {
          newValues[field.field_key] = field.default_value;
        }
      });

      setValues(newValues);
      setFieldErrors({});
    } else {
      // No fields, clear values
      setValues({});
      setFieldErrors({});
    }
  }, [formFields]);

  // Notify parent of value changes
  useEffect(() => {
    if (onSpecificationsChange) {
      // Extract standard variant fields
      const colour_code = values.colour_code || values.colour || null;
      const size_code = values.size_code || values.size || null;
      const uom_code = values.uom_code || values.uom || null;
      const vendor_code = values.vendor_code || values.vendor || null;

      // Extract custom field values
      const custom_field_values = {};
      Object.keys(values).forEach(key => {
        if (!['colour_code', 'size_code', 'uom_code', 'vendor_code', 'colour', 'size', 'uom', 'vendor'].includes(key)) {
          custom_field_values[key] = values[key];
        }
      });

      onSpecificationsChange({
        colour_code,
        size_code,
        uom_code,
        vendor_code,
        custom_field_values
      });
    }
  }, [values, onSpecificationsChange]);

  const handleFieldChange = (fieldKey, value) => {
    setValues(prev => ({
      ...prev,
      [fieldKey]: value
    }));

    // Clear error for this field
    if (fieldErrors[fieldKey]) {
      setFieldErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldKey];
        return newErrors;
      });
    }
  };

  const validateFields = () => {
    const errors = {};

    formFields.forEach(field => {
      if (field.required) {
        const value = values[field.field_key];
        if (!value || value === '') {
          errors[field.field_key] = `${field.field_name} is required`;
        }
      }
    });

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Expose validation method to parent
  useEffect(() => {
    if (window.validateSpecifications) {
      window.validateSpecifications = validateFields;
    }
  }, [formFields, values]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg border p-6">
        {showTitle && (
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Specifications</h3>
        )}
        <div className="text-center py-8 text-gray-500">
          Loading specifications...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border p-6">
        {showTitle && (
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Specifications</h3>
        )}
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Error loading specifications</p>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!categoryCode) {
    return (
      <div className="bg-white rounded-lg border p-6">
        {showTitle && (
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Specifications</h3>
        )}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            Please select a category first to view applicable specifications.
          </p>
        </div>
      </div>
    );
  }

  if (!formFields || formFields.length === 0) {
    return (
      <div className="bg-white rounded-lg border p-6">
        {showTitle && (
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Specifications</h3>
        )}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            No specifications configured for this category.
          </p>
          <p className="text-xs text-blue-600 mt-1">
            Contact your administrator to configure specifications for this category.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      {showTitle && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Specifications</h3>
          <p className="text-sm text-gray-600 mt-1">
            Configure specifications for this item based on its category
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {formFields.map((field) => (
          <FieldInput
            key={field.field_key}
            field={field}
            value={values[field.field_key]}
            onChange={handleFieldChange}
            categoryCode={categoryCode}
            error={fieldErrors[field.field_key]}
          />
        ))}
      </div>

      {/* Info about required fields */}
      {formFields.some(f => f.required) && (
        <div className="mt-4 text-xs text-gray-500">
          <span className="text-red-500">*</span> Required fields
        </div>
      )}
    </div>
  );
};

export default DynamicSpecificationForm;
