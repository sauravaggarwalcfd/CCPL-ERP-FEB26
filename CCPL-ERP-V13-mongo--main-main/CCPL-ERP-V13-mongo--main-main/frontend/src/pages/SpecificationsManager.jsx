/**
 * Specifications Manager Page
 * Admin interface to configure specifications for item categories
 */

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Save, AlertCircle } from 'lucide-react';
import { useLayout } from '../context/LayoutContext';
import VariantFieldToggle from '../components/specifications/VariantFieldToggle';
import CustomFieldConfig from '../components/specifications/CustomFieldConfig';
import { specificationApi } from '../services/specificationApi';
import { colourApi, sizeApi, uomApi } from '../services/variantApi';

const SpecificationsManager = () => {
  const { setTitle } = useLayout();
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [specifications, setSpecifications] = useState(null);
  const [variantGroups, setVariantGroups] = useState({
    colour: [],
    size: [],
    uom: []
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Load categories on mount
  useEffect(() => {
    setTitle('Specifications Manager');
    loadCategories();
    loadVariantGroups();
  }, [setTitle]);

  // Load specifications when category changes
  useEffect(() => {
    if (selectedCategory) {
      loadSpecifications();
    } else {
      setSpecifications(null);
    }
  }, [selectedCategory]);

  const loadCategories = async () => {
    try {
      // TODO: Replace with actual category API call
      // For now, using mock data
      setCategories([
        { code: 'THREAD', name: 'Threads' },
        { code: 'FABRIC', name: 'Fabrics' },
        { code: 'BUTTON', name: 'Buttons' },
        { code: 'LABEL', name: 'Labels' },
        { code: 'ZIPPER', name: 'Zippers' }
      ]);
    } catch (error) {
      console.error('Error loading categories:', error);
      toast.error('Failed to load categories');
    }
  };

  const loadVariantGroups = async () => {
    try {
      const [colourRes, sizeRes, uomRes] = await Promise.all([
        colourApi.getGroups(),
        sizeApi.getGroups(),
        uomApi.getGroups()
      ]);

      setVariantGroups({
        colour: colourRes.data || [],
        size: sizeRes.data || [],
        uom: uomRes.data || []
      });
    } catch (error) {
      console.error('Error loading variant groups:', error);
    }
  };

  const loadSpecifications = async () => {
    try {
      setLoading(true);
      const response = await specificationApi.get(selectedCategory);
      setSpecifications(response.data);
      setHasChanges(false);
    } catch (error) {
      if (error.response?.status === 404) {
        // No specifications configured yet - create default
        setSpecifications({
          category_code: selectedCategory,
          category_name: categories.find(c => c.code === selectedCategory)?.name || selectedCategory,
          category_level: 1,
          specifications: {
            colour: null,
            size: null,
            uom: null,
            vendor: null
          },
          custom_fields: []
        });
        setHasChanges(false);
      } else {
        console.error('Error loading specifications:', error);
        toast.error('Failed to load specifications');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVariantFieldUpdate = (fieldKey, config) => {
    setSpecifications(prev => ({
      ...prev,
      specifications: {
        ...prev.specifications,
        [fieldKey]: config
      }
    }));
    setHasChanges(true);
  };

  const handleAddCustomField = (fieldData) => {
    setSpecifications(prev => ({
      ...prev,
      custom_fields: [...prev.custom_fields, fieldData]
    }));
    setHasChanges(true);
    toast.success('Custom field added');
  };

  const handleUpdateCustomField = (fieldCode, fieldData) => {
    setSpecifications(prev => ({
      ...prev,
      custom_fields: prev.custom_fields.map(field =>
        field.field_code === fieldCode ? fieldData : field
      )
    }));
    setHasChanges(true);
    toast.success('Custom field updated');
  };

  const handleDeleteCustomField = (fieldCode) => {
    if (!confirm(`Are you sure you want to delete the custom field "${fieldCode}"?`)) {
      return;
    }

    setSpecifications(prev => ({
      ...prev,
      custom_fields: prev.custom_fields.filter(field => field.field_code !== fieldCode)
    }));
    setHasChanges(true);
    toast.success('Custom field deleted');
  };

  const handleSave = async () => {
    if (!specifications) return;

    try {
      setSaving(true);

      // Prepare data for API
      const data = {
        category_code: specifications.category_code,
        category_name: specifications.category_name,
        category_level: specifications.category_level,
        specifications: {},
        custom_fields: specifications.custom_fields
      };

      // Add variant field configurations
      ['colour', 'size', 'uom', 'vendor'].forEach(field => {
        if (specifications.specifications[field]) {
          data.specifications[field] = specifications.specifications[field];
        }
      });

      await specificationApi.createOrUpdate(selectedCategory, data);
      toast.success('Specifications saved successfully');
      setHasChanges(false);
      loadSpecifications(); // Reload to get server state
    } catch (error) {
      console.error('Error saving specifications:', error);
      let message = 'Failed to save specifications';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          message = error.response.data.detail.map(err => err.msg).join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          message = error.response.data.detail;
        }
      }
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Sticky Top Bar */}
      <div className="bg-white p-4 border-b flex items-center justify-between sticky top-0 z-10 gap-4">
        <div className="flex-1 max-w-md">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">-- Select a Category --</option>
            {categories.map((cat) => (
              <option key={cat.code} value={cat.code}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-4">
          {hasChanges && (
            <span className="text-sm text-orange-600 font-medium">
              Unsaved changes
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={saving || !hasChanges}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              saving || !hasChanges
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
            }`}
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          {loading ? (
            <div className="bg-white rounded-lg border p-12 text-center">
              <p className="text-gray-500">Loading specifications...</p>
            </div>
          ) : !selectedCategory ? (
            <div className="bg-white rounded-lg border p-12 text-center">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Select a category to configure its specifications</p>
            </div>
          ) : specifications ? (
            <div className="space-y-6">
              {/* Variant Fields Section */}
              <div className="bg-white rounded-lg border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Variant Fields (Standard)
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  Enable or disable standard variant fields for this category.
                  Only enabled fields will appear in the Item Master form.
                </p>

                <div className="space-y-4">
                  <VariantFieldToggle
                    field="Colour"
                    fieldKey="colour"
                    config={specifications.specifications?.colour}
                    groups={variantGroups.colour}
                    onUpdate={handleVariantFieldUpdate}
                  />

                  <VariantFieldToggle
                    field="Size"
                    fieldKey="size"
                    config={specifications.specifications?.size}
                    groups={variantGroups.size}
                    onUpdate={handleVariantFieldUpdate}
                  />

                  <VariantFieldToggle
                    field="UOM (Unit of Measure)"
                    fieldKey="uom"
                    config={specifications.specifications?.uom}
                    groups={variantGroups.uom}
                    onUpdate={handleVariantFieldUpdate}
                  />

                  <VariantFieldToggle
                    field="Vendor/Brand"
                    fieldKey="vendor"
                    config={specifications.specifications?.vendor}
                    groups={[]}
                    onUpdate={handleVariantFieldUpdate}
                  />
                </div>
              </div>

              {/* Custom Fields Section */}
              <div className="bg-white rounded-lg border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Custom Fields
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  Add category-specific custom fields such as Quality Grade, Material, GSM, etc.
                </p>

                <CustomFieldConfig
                  customFields={specifications.custom_fields || []}
                  onAdd={handleAddCustomField}
                  onUpdate={handleUpdateCustomField}
                  onDelete={handleDeleteCustomField}
                />
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default SpecificationsManager;
