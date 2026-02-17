/**
 * Grouped Variant List Component
 * Displays variant items grouped by their categories
 */
import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

const GroupedVariantList = ({ groupedItems, groups, renderItem, emptyMessage }) => {
  const groupKeys = Object.keys(groupedItems);
  // Track collapsed state (true = collapsed)
  const [collapsedGroups, setCollapsedGroups] = useState({});

  if (groupKeys.length === 0) {
    return (
      <div className="bg-white rounded-lg border p-12 text-center text-gray-500">
        {emptyMessage || 'No items found'}
      </div>
    );
  }

  // Get group name from code
  const getGroupName = (groupCode) => {
    const group = groups.find((g) => g.code === groupCode || g.value === groupCode);
    return group ? group.name : groupCode;
  };

  const toggleGroup = (groupKey) => {
    setCollapsedGroups(prev => ({
      ...prev,
      [groupKey]: !prev[groupKey]
    }));
  };

  return (
    <div className="space-y-6">
      {groupKeys.map((groupKey) => {
        const items = groupedItems[groupKey];
        const groupName = getGroupName(groupKey);
        const isCollapsed = collapsedGroups[groupKey];

        return (
          <div key={groupKey} className="bg-white rounded-lg border overflow-hidden">
            {/* Group Header */}
            <div 
              className="bg-gray-50 px-4 py-3 border-b cursor-pointer hover:bg-gray-100 transition-colors"
              onClick={() => toggleGroup(groupKey)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {isCollapsed ? <ChevronRight size={20} className="text-gray-500" /> : <ChevronDown size={20} className="text-gray-500" />}
                  <h3 className="font-semibold text-gray-900">{groupName}</h3>
                </div>
                <span className="text-sm text-gray-500">{items.length} items</span>
              </div>
            </div>

            {/* Group Items */}
            {!isCollapsed && (
              <div className="p-4 space-y-2">
                {items.map((item) => (
                  <div key={item.id || item.colour_code || item.size_code || item.uom_code}>
                    {renderItem(item)}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default GroupedVariantList;
