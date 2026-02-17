# Drag-and-Drop Feature for Category Hierarchy

## Overview
Added comprehensive drag-and-drop functionality to `ItemCategoryHierarchy.jsx` allowing users to reorganize categories by dragging and dropping them onto new parent categories.

## Features Implemented

### 1. **Draggable Items**
- All category items are now draggable
- Cursor changes to `grab` on hover and `grabbing` while dragging
- Visual feedback with 50% opacity while dragging
- Small Move icon appears on hover to indicate draggable items

### 2. **Drop Zone Validation**
- **Green highlight**: Valid drop zone (category can be moved here)
- **Red highlight**: Invalid drop zone (cannot move - would create circular reference)
- **Scale effect**: Drop zone slightly enlarges when valid
- Real-time validation during drag operation

### 3. **Smart Validation Logic**
- **Prevents moving parent into its own child** - Uses recursive descendant checking
- **Prevents dropping on self** - Cannot drop a category on itself
- **Validates hierarchy integrity** - Ensures no circular references

### 4. **Warning Modal**
Before any move operation, a comprehensive warning modal appears showing:
- Clear explanation of what will happen
- Details of the move operation:
  - Source category name and level
  - Target (new parent) category name and level
  - New level after the move
- Warning points:
  - Changes parent-child relationship
  - Updates level of moved category
  - May affect all child categories
  - Updates structure immediately

### 5. **API Integration**
- Uses existing PUT endpoint: `/api/items/categories/{category_id}`
- Updates:
  - `parent_category_id`
  - `parent_category_name`
  - `level` (automatically calculated as target level + 1)
- Preserves all other category properties
- Refreshes hierarchy after successful move

### 6. **Visual Indicators**
- **Header notification**: "Drag & drop to reorganize" with Move icon
- **Drag icon**: Small move icon on each item (visible on hover)
- **Toast notifications**:
  - "Dragging: {category_name}" when drag starts
  - Success message after move completes
  - Error messages for invalid operations
- **Color coding**:
  - Green = Valid drop zone
  - Red = Invalid drop zone

## State Management

### New State Variables
```javascript
const [draggedNode, setDraggedNode] = useState(null)      // Currently dragged category
const [dragOverNode, setDragOverNode] = useState(null)    // Category being hovered over
const [isDragValid, setIsDragValid] = useState(false)     // Is current drop position valid?
const [showMoveWarning, setShowMoveWarning] = useState(false)  // Show warning modal?
const [pendingMove, setPendingMove] = useState(null)      // Pending move operation details
```

## Helper Functions Added

### 1. `isDescendant(parentId, childId)`
Recursively checks if a category is a descendant of another category to prevent circular references.

### 2. `canDropOn(draggedNode, targetNode)`
Validates if a category can be dropped on another category:
- Returns false if trying to drop on itself
- Returns false if trying to drop parent into its own descendant
- Returns true for valid drops

### 3. Drag Event Handlers
- `handleDragStart(e, node)` - Initiates drag, sets visual feedback
- `handleDragOver(e, node)` - Validates drop zone, shows green/red highlight
- `handleDragLeave(e)` - Clears drop zone highlight
- `handleDrop(e, targetNode)` - Shows warning modal for confirmed moves
- `handleDragEnd(e)` - Resets visual state

### 4. Move Operation Handlers
- `confirmMove()` - Executes the API call to update the category
- `cancelMove()` - Cancels the pending move operation
- `resetDragState()` - Clears all drag-related state

## Usage Instructions

### How to Move Categories:
1. **Hover** over any category item - you'll see a small move icon appear
2. **Click and hold** to start dragging - cursor changes to grabbing hand
3. **Drag** over another category to see if it's a valid drop zone:
   - **Green** = Valid - you can drop here
   - **Red** = Invalid - cannot drop here (would create circular reference)
4. **Release** to drop - a warning modal will appear
5. **Review** the move details in the modal
6. **Click "Confirm Move"** to execute, or **"Cancel"** to abort

### What Gets Updated:
- The dragged category's parent is changed to the target category
- The level is automatically recalculated
- All child categories are affected (their paths update)
- The hierarchy refreshes automatically

### Restrictions:
- Cannot move a category onto itself
- Cannot move a parent category into its own child (prevents loops)
- Cannot move a category if it would create an invalid hierarchy

## Technical Details

### HTML5 Drag and Drop API
Uses native browser drag-and-drop with proper event handling:
- `draggable` attribute on each category item
- Full event chain: dragstart → dragover → drop → dragend
- Data transfer with `effectAllowed = 'move'`

### CSS Classes for Visual Feedback
```javascript
// Valid drop zone
'bg-green-200 border-2 border-green-500 scale-105'

// Invalid drop zone
'bg-red-200 border-2 border-red-500'

// Dragging item
'opacity-50'

// Draggable cursor
'cursor-grab active:cursor-grabbing'
```

### API Request Format
```javascript
PUT /api/items/categories/{category_id}
{
  ...existingCategoryData,
  parent_category_id: targetCategory.category_id,
  parent_category_name: targetCategory.category_name,
  level: targetCategory.level + 1
}
```

## Safety Features

1. **Validation before API call** - Double-checks validity before sending request
2. **Warning modal** - User must explicitly confirm the move
3. **Detailed move information** - Shows exactly what will happen
4. **Error handling** - Catches and displays API errors
5. **Automatic refresh** - Ensures UI stays in sync with database
6. **Toast notifications** - Clear feedback for all operations

## Icons Used
- `Move` - Drag indicator and modal icon
- `AlertTriangle` - Warning modal header
- Existing: `FolderTree`, `FolderOpen`, `Folder`, `Plus`, `ChevronRight`, `ChevronDown`, `Trash2`

## Browser Compatibility
Works with all modern browsers supporting HTML5 Drag and Drop API:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

---

**Note**: This feature seamlessly integrates with existing category management functionality. All original features (create, edit, delete, search, filter) continue to work as before.
