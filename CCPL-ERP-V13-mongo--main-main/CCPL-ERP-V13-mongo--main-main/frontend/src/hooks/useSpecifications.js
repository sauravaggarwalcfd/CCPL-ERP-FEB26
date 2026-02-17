/**
 * useSpecifications Hook
 * Fetches and manages specification configuration for a category
 */

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { specificationApi } from '../services/specificationApi';

/**
 * Hook to fetch and manage category specifications
 * @param {string} categoryCode - The category code to fetch specifications for
 * @param {boolean} autoFetch - Whether to automatically fetch on mount (default: true)
 * @returns {object} - { specifications, formFields, loading, error, refetch }
 */
export const useSpecifications = (categoryCode, autoFetch = true) => {
  const [specifications, setSpecifications] = useState(null);
  const [formFields, setFormFields] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSpecifications = useCallback(async () => {
    if (!categoryCode) {
      setSpecifications(null);
      setFormFields([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Fetch specification configuration
      const specResponse = await specificationApi.get(categoryCode);
      setSpecifications(specResponse.data);

      // Fetch form fields for rendering
      const fieldsResponse = await specificationApi.getFormFields(categoryCode);
      setFormFields(fieldsResponse.data || []);
    } catch (err) {
      console.error('Error fetching specifications:', err);

      // If not found, that's okay - no specifications configured yet
      if (err.response?.status === 404) {
        setSpecifications(null);
        setFormFields([]);
        setError(null);
      } else {
        setError(err.message || 'Failed to fetch specifications');
        toast.error('Failed to load specifications');
      }
    } finally {
      setLoading(false);
    }
  }, [categoryCode]);

  useEffect(() => {
    if (autoFetch && categoryCode) {
      fetchSpecifications();
    }
  }, [categoryCode, autoFetch, fetchSpecifications]);

  return {
    specifications,
    formFields,
    loading,
    error,
    refetch: fetchSpecifications
  };
};

/**
 * Hook to fetch field values/options for a specific field
 * @param {string} categoryCode - The category code
 * @param {string} fieldKey - The field key (colour, size, uom, vendor, or custom field)
 * @param {boolean} autoFetch - Whether to automatically fetch on mount (default: true)
 * @returns {object} - { options, loading, error, refetch }
 */
export const useFieldValues = (categoryCode, fieldKey, autoFetch = true) => {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchFieldValues = useCallback(async () => {
    if (!categoryCode || !fieldKey) {
      setOptions([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await specificationApi.getFieldValues(categoryCode, fieldKey);
      setOptions(response.data || []);
    } catch (err) {
      console.error('Error fetching field values:', err);
      setError(err.message || 'Failed to fetch field values');
      setOptions([]);
    } finally {
      setLoading(false);
    }
  }, [categoryCode, fieldKey]);

  useEffect(() => {
    if (autoFetch && categoryCode && fieldKey) {
      fetchFieldValues();
    }
  }, [categoryCode, fieldKey, autoFetch, fetchFieldValues]);

  return {
    options,
    loading,
    error,
    refetch: fetchFieldValues
  };
};

/**
 * Hook to manage item specifications
 * @param {string} itemCode - The item code
 * @returns {object} - { itemSpecifications, loading, error, save, refetch }
 */
export const useItemSpecifications = (itemCode) => {
  const [itemSpecifications, setItemSpecifications] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchItemSpecifications = useCallback(async () => {
    if (!itemCode) {
      setItemSpecifications(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await specificationApi.item.get(itemCode);
      setItemSpecifications(response.data);
    } catch (err) {
      console.error('Error fetching item specifications:', err);

      // If not found, that's okay - no specifications yet
      if (err.response?.status === 404) {
        setItemSpecifications(null);
        setError(null);
      } else {
        setError(err.message || 'Failed to fetch item specifications');
      }
    } finally {
      setLoading(false);
    }
  }, [itemCode]);

  const saveItemSpecifications = async (categoryCode, data) => {
    if (!itemCode) return;

    try {
      setLoading(true);
      setError(null);

      const response = await specificationApi.item.createOrUpdate(
        itemCode,
        categoryCode,
        data
      );
      setItemSpecifications(response.data);
      toast.success('Specifications saved successfully');
      return response.data;
    } catch (err) {
      console.error('Error saving item specifications:', err);
      const message = err.response?.data?.detail || 'Failed to save specifications';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (itemCode) {
      fetchItemSpecifications();
    }
  }, [itemCode, fetchItemSpecifications]);

  return {
    itemSpecifications,
    loading,
    error,
    save: saveItemSpecifications,
    refetch: fetchItemSpecifications
  };
};

export default useSpecifications;
