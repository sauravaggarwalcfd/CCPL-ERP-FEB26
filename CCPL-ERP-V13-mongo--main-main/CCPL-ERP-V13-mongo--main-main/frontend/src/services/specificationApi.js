/**
 * Specifications API Service
 * Handles all API calls for category and item specifications
 */

import api from './api';

// ==================== CATEGORY SPECIFICATIONS ====================

export const specificationApi = {
  // List all category specifications
  list: (params = {}) => api.get('/specifications', { params }),

  // Get specification configuration for a category
  get: (categoryCode) => api.get(`/specifications/${categoryCode}`),

  // Create or update specifications for a category
  createOrUpdate: (categoryCode, data) =>
    api.post(`/specifications/${categoryCode}`, data),

  // Update a specific variant field (colour, size, uom, vendor)
  updateVariantField: (categoryCode, field, config) =>
    api.put(`/specifications/${categoryCode}/variant/${field}`, config),

  // Delete (disable) a variant field
  deleteVariantField: (categoryCode, field) =>
    api.delete(`/specifications/${categoryCode}/variant/${field}`),

  // Add a custom field
  addCustomField: (categoryCode, fieldConfig) =>
    api.post(`/specifications/${categoryCode}/custom-field`, fieldConfig),

  // Update a custom field
  updateCustomField: (categoryCode, fieldCode, fieldConfig) =>
    api.put(`/specifications/${categoryCode}/custom-field/${fieldCode}`, fieldConfig),

  // Delete a custom field
  deleteCustomField: (categoryCode, fieldCode) =>
    api.delete(`/specifications/${categoryCode}/custom-field/${fieldCode}`),

  // Get all form fields for a category (for rendering)
  getFormFields: (categoryCode) =>
    api.get(`/specifications/${categoryCode}/form-fields`),

  // Get field values/options for a specific field
  getFieldValues: (categoryCode, fieldKey) =>
    api.get(`/specifications/${categoryCode}/field-values/${fieldKey}`),
};

// ==================== ITEM SPECIFICATIONS ====================

export const itemSpecificationApi = {
  // Get specifications for a specific item
  get: (itemCode) => api.get(`/items/${itemCode}/specifications`),

  // Create or update specifications for an item
  createOrUpdate: (itemCode, categoryCode, data) =>
    api.post(`/items/${itemCode}/specifications`, data, {
      params: { category_code: categoryCode }
    }),

  // Delete specifications for an item
  delete: (itemCode) => api.delete(`/items/${itemCode}/specifications`),

  // Query items by specifications
  queryBySpecifications: (params) =>
    api.get('/items/by-specifications', { params }),
};

// ==================== COMBINED API ====================

// Export combined API object
const specificationsApi = {
  category: specificationApi,
  item: itemSpecificationApi,
};

export default specificationsApi;
