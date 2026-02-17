/**
 * Colour Preview Component
 * Modal for previewing colour with hex and RGB values
 */

import { X } from 'lucide-react';

const ColourPreview = ({ colour, onClose }) => {
  if (!colour) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Colour Preview</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Colour Swatch */}
          <div
            className="w-full h-48 rounded-lg border-2 border-gray-300 shadow-inner"
            style={{ backgroundColor: colour.colour_hex }}
          />

          {/* Colour Info */}
          <div className="space-y-3">
            <div>
              <div className="text-sm font-medium text-gray-500">Name</div>
              <div className="text-lg font-semibold text-gray-900">
                {colour.colour_name}
              </div>
            </div>

            <div>
              <div className="text-sm font-medium text-gray-500">Code</div>
              <div className="text-lg font-mono text-gray-900">{colour.colour_code}</div>
            </div>

            <div>
              <div className="text-sm font-medium text-gray-500">Hex Value</div>
              <div className="text-lg font-mono text-gray-900">{colour.colour_hex}</div>
            </div>

            {colour.rgb_value && (
              <div>
                <div className="text-sm font-medium text-gray-500">RGB Value</div>
                <div className="text-lg font-mono text-gray-900">
                  rgb({colour.rgb_value.r}, {colour.rgb_value.g},{' '}
                  {colour.rgb_value.b})
                </div>
              </div>
            )}

            <div>
              <div className="text-sm font-medium text-gray-500">Group</div>
              <div className="text-lg text-gray-900">{colour.group_name}</div>
            </div>

            {colour.description && (
              <div>
                <div className="text-sm font-medium text-gray-500">Description</div>
                <div className="text-gray-900">{colour.description}</div>
              </div>
            )}
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

export default ColourPreview;
