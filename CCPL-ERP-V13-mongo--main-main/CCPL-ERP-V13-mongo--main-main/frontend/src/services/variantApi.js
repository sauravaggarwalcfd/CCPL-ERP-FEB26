/**
 * Variant Master API Service
 * Handles all API calls for Colour, Size, UOM, and Variant Groups
 */

import api from './api';

// ==================== COLOUR API ====================

export const colourApi = {
  // List all colours with optional filters
  list: (params = {}) => api.get('/colours', { params }),

  // Get colours by group
  getByGroup: (group) => api.get(`/colours/group/${group}`),

  // Get all colour groups
  getGroups: () => api.get('/colours/groups'),

  // Get single colour by code
  get: (code) => api.get(`/colours/${code}`),

  // Create new colour
  create: (data) => api.post('/colours', data),

  // Update existing colour
  update: (code, data) => api.put(`/colours/${code}`, data),

  // Delete (soft delete) colour
  delete: (code) => api.delete(`/colours/${code}`),

  // Preview hex colour
  previewHex: (hex) => api.get(`/colours/hex-preview/${hex}`),
};

// ==================== SIZE API ====================

export const sizeApi = {
  // List all sizes with optional filters
  list: (params = {}) => api.get('/sizes', { params }),

  // Get sizes by group
  getByGroup: (group) => api.get(`/sizes/group/${group}`),

  // Get all size groups
  getGroups: () => api.get('/sizes/groups'),

  // Get single size by code
  get: (code) => api.get(`/sizes/${code}`),

  // Create new size
  create: (data) => api.post('/sizes', data),

  // Update existing size
  update: (code, data) => api.put(`/sizes/${code}`, data),

  // Delete (soft delete) size
  delete: (code) => api.delete(`/sizes/${code}`),
};

// ==================== UOM API ====================

export const uomApi = {
  // List all UOMs with optional filters
  list: (params = {}) => api.get('/uoms', { params }),

  // Get UOMs by group
  getByGroup: (group) => api.get(`/uoms/group/${group}`),

  // Get all UOM groups
  getGroups: () => api.get('/uoms/groups'),

  // Get single UOM by code
  get: (code) => api.get(`/uoms/${code}`),

  // Create new UOM
  create: (data) => api.post('/uoms', data),

  // Update existing UOM
  update: (code, data) => api.put(`/uoms/${code}`, data),

  // Delete (soft delete) UOM
  delete: (code) => api.delete(`/uoms/${code}`),

  // Convert value between UOMs
  convert: (fromCode, toCode, value) =>
    api.get(`/uoms/convert/${fromCode}/${toCode}`, { params: { value } }),
};

// ==================== VARIANT GROUPS API ====================

export const variantGroupApi = {
  // List all variant groups with optional filters
  list: (params = {}) => api.get('/variant-groups', { params }),

  // Get variant groups by type (COLOUR, SIZE, UOM)
  getByType: (variantType) => api.get(`/variant-groups/type/${variantType}`),

  // Get all variant types
  getTypes: () => api.get('/variant-groups/types'),

  // Get single variant group by code
  get: (groupCode) => api.get(`/variant-groups/${groupCode}`),

  // Get summary of all groups organized by type
  getSummary: () => api.get('/variant-groups/summary/all'),

  // Create new variant group
  create: (data) => api.post('/variant-groups', data),

  // Update existing variant group
  update: (groupCode, data) => api.put(`/variant-groups/${groupCode}`, data),

  // Delete variant group
  delete: (groupCode) => api.delete(`/variant-groups/${groupCode}`),
};

// ==================== COMBINED API ====================

// Export combined variant API object
const variantApi = {
  colours: colourApi,
  sizes: sizeApi,
  uoms: uomApi,
  groups: variantGroupApi,
};

export default variantApi;
