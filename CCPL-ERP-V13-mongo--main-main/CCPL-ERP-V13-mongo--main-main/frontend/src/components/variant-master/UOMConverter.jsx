/**
 * UOM Converter Component
 * Modal for converting values between UOMs
 */

import { useState } from 'react';
import { X, ArrowRight } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { uomApi } from '../../services/variantApi';

const UOMConverter = ({ uoms, onClose }) => {
  const [fromUOM, setFromUOM] = useState('');
  const [toUOM, setToUOM] = useState('');
  const [value, setValue] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Get unique groups
  const groups = [...new Set(uoms.map((uom) => uom.uom_group))];

  // Filter UOMs by group for from selection
  const fromUOMGroup = fromUOM ? uoms.find((u) => u.uom_code === fromUOM)?.uom_group : null;
  const toUOMsList = fromUOMGroup
    ? uoms.filter((u) => u.uom_group === fromUOMGroup)
    : [];

  const handleConvert = async () => {
    if (!fromUOM || !toUOM || !value) {
      toast.error('Please fill in all fields');
      return;
    }

    if (fromUOM === toUOM) {
      toast.error('Please select different UOMs');
      return;
    }

    try {
      setLoading(true);
      const response = await uomApi.convert(fromUOM, toUOM, parseFloat(value));
      setResult(response.data);
    } catch (error) {
      console.error('Error converting:', error);
      let message = 'Conversion failed';
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      }
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFromUOM('');
    setToUOM('');
    setValue('');
    setResult(null);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">UOM Converter</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Converter Form */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            {/* From UOM */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                From UOM
              </label>
              <select
                value={fromUOM}
                onChange={(e) => {
                  setFromUOM(e.target.value);
                  setToUOM('');
                  setResult(null);
                }}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select UOM</option>
                {groups.map((group) => (
                  <optgroup key={group} label={group}>
                    {uoms
                      .filter((u) => u.uom_group === group)
                      .map((uom) => (
                        <option key={uom.uom_code} value={uom.uom_code}>
                          {uom.uom_name} ({uom.uom_symbol})
                        </option>
                      ))}
                  </optgroup>
                ))}
              </select>
            </div>

            {/* Value */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Value
              </label>
              <input
                type="number"
                value={value}
                onChange={(e) => {
                  setValue(e.target.value);
                  setResult(null);
                }}
                step="0.01"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter value"
              />
            </div>

            {/* To UOM */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                To UOM
              </label>
              <select
                value={toUOM}
                onChange={(e) => {
                  setToUOM(e.target.value);
                  setResult(null);
                }}
                disabled={!fromUOM}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              >
                <option value="">Select UOM</option>
                {toUOMsList.map((uom) => (
                  <option key={uom.uom_code} value={uom.uom_code}>
                    {uom.uom_name} ({uom.uom_symbol})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Convert Button */}
          <div className="flex gap-3">
            <button
              onClick={handleConvert}
              disabled={!fromUOM || !toUOM || !value || loading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {loading ? 'Converting...' : 'Convert'}
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              Reset
            </button>
          </div>

          {/* Result */}
          {result && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center justify-center gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">
                    {result.from_value}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">{result.from_uom}</div>
                </div>

                <ArrowRight className="w-8 h-8 text-green-600" />

                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {result.to_value.toFixed(6)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">{result.to_uom}</div>
                </div>
              </div>

              <div className="mt-4 text-center text-sm text-gray-600">
                Conversion Factor: {result.conversion_factor.toFixed(6)}
              </div>
            </div>
          )}

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              <strong>Note:</strong> Conversion only works between UOMs in the same
              group (e.g., Weight to Weight, Length to Length).
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default UOMConverter;
