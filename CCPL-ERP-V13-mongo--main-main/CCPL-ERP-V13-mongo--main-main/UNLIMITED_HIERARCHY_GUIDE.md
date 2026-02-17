# Item Category - Unlimited Hierarchy Guide

## Overview
Your Item Category system now supports **UNLIMITED NESTING LEVELS** - you can create categories as deep as you need!

## How It Works

### Parent-Child Relationships
- Each category can have a `parent_category_id` that links it to its parent
- Categories without a parent (`parent_category_id = null`) are root-level categories
- Any category can have unlimited children
- Children can have their own children, forming infinite depth

### Level Tracking
- `level` field automatically tracks the depth in the tree
- Level 1 = Root categories (no parent)
- Level 2 = Direct children of root
- Level 3 = Grandchildren
- Level 4, 5, 6... = Unlimited depth

## Example Hierarchies

### Simple 3-Level Structure
```
📁 RAW MATERIALS (L1)
  ├─ 📁 FABRICS (L2)
  │   ├─ 📄 COTTON (L3)
  │   ├─ 📄 POLYESTER (L3)
  │   └─ 📄 SILK (L3)
  └─ 📁 THREADS (L2)
      ├─ 📄 COTTON THREAD (L3)
      └─ 📄 POLY THREAD (L3)
```

### Complex Multi-Level Structure (Unlimited)
```
📁 RAW MATERIALS (L1)
  └─ 📁 FABRICS (L2)
      └─ 📁 COTTON FABRICS (L3)
          └─ 📁 ORGANIC COTTON (L4)
              └─ 📁 CERTIFIED ORGANIC (L5)
                  └─ 📁 PREMIUM GRADE (L6)
                      └─ 📁 EXPORT QUALITY (L7)
                          └─ ... unlimited depth
```

### Multiple Branches at Same Level
```
📁 FINISHED GOODS (L1)
  ├─ 📁 MENS WEAR (L2)
  │   ├─ 📁 T-SHIRTS (L3)
  │   │   ├─ 📄 CREW NECK (L4)
  │   │   ├─ 📄 V-NECK (L4)
  │   │   └─ 📄 POLO (L4)
  │   └─ 📁 SHIRTS (L3)
  │       ├─ 📄 CASUAL (L4)
  │       └─ 📄 FORMAL (L4)
  └─ 📁 WOMENS WEAR (L2)
      ├─ 📁 TOPS (L3)
      └─ 📁 DRESSES (L3)
```

## UI Features

### Visual Indicators
- **Level Badge**: Shows "L1", "L2", "L3", etc. next to each category
- **Child Count**: Blue badge shows number of direct children
- **Indentation**: Each level is indented 20px for clear hierarchy
- **Icons**: 
  - Folders (📁) for categories with children
  - Dots (•) for leaf categories

### Operations

#### Creating Root Category (Level 1)
1. Click "New Category" button
2. Fill in details
3. Leave parent empty
4. Saves as Level 1

#### Adding Child Category (Any Level)
1. Click **+ icon** next to any category
2. Form pre-fills with parent info
3. Level automatically increments (parent level + 1)
4. Inherits inventory_class and UOMs from parent

#### Editing Categories
- Click any category to edit
- Can change properties but not parent/level (to maintain tree integrity)
- Changes to inventory_class propagate to all descendants

#### Moving Categories
- Delete and recreate under new parent (safe approach)
- Maintains data integrity

## Best Practices

### When to Add Levels
✅ **Good Use Cases:**
- Different material specifications (Cotton → Organic Cotton → Premium Organic)
- Product variations (Shirts → Casual Shirts → Hawaiian Shirts → Vintage Hawaiian)
- Geographic/brand subdivisions (Asia Region → India → Mumbai)
- Quality grades (Standard → Premium → Super Premium)

❌ **Avoid Over-Nesting:**
- Don't create levels just for organization
- If 3-4 levels suffice, don't force deeper
- Consider if attributes/tags might work better than levels

### Naming Conventions
- **Level 1**: Broad categories (RAW MATERIALS, FINISHED GOODS)
- **Level 2**: Major types (FABRICS, ACCESSORIES)
- **Level 3+**: Specific materials or products (COTTON, BUTTONS)
- Keep names clear and distinctive at each level

### Code Format
- Use 2-4 letter codes
- Make them meaningful: FABR (Fabrics), COTT (Cotton)
- Uppercase only (enforced automatically)

## Technical Details

### Database Structure
```javascript
{
  category_id: "ORGCOT",           // Unique ID
  category_name: "ORGANIC COTTON", // Display name
  category_code: "ORGC",           // Short code
  parent_category_id: "COTT",      // Links to parent
  parent_category_name: "COTTON",  // Denormalized
  level: 4,                        // Auto-calculated depth
  inventory_class: "raw_materials",// Inherited from root
  selected_uoms: ["KGS", "MTR"],   // Multiple UOMs
  // ... other fields
}
```

### Validation Rules
1. **Inventory Class** (required): Must be set for all categories
2. **UOMs** (required): At least one unit of measure
3. **Category Code** (required): 1-4 uppercase letters only
4. **Category Name** (required): Auto-uppercase
5. **No Duplicates**: Category codes must be unique across all levels
6. **Parent Validation**: Cannot set self as parent (prevents loops)

### Inheritance
When you create a child category:
- `inventory_class` → Inherited from parent
- `selected_uoms` → Inherited from parent (can modify)
- `level` → Parent level + 1 (auto-calculated)

When you change parent's `inventory_class`:
- ⚠️ Warning shown if parent has children
- All children automatically updated with new class

## Migration from Old Structure

### If You Had ItemSubCategory Model:
Old 2-tier system:
- ItemCategory (Level 1)
- ItemSubCategory (Level 2)

New unlimited system:
- Everything is ItemCategory
- Use `parent_category_id` to create relationships
- Level 2 categories are just children of Level 1
- Can go deeper (Level 3, 4, 5...)

### Data Migration:
```javascript
// Old ItemSubCategory
{
  sub_category_id: "TSHRT",
  sub_category_name: "T-Shirt",
  category_id: "CLOTH"  // parent reference
}

// New ItemCategory (child)
{
  category_id: "TSHRT",
  category_name: "T-SHIRT",
  parent_category_id: "CLOTH",  // same reference
  level: 2,  // child level
  inventory_class: "finished_goods",  // inherited
}
```

## API Endpoints

### Get Categories (Tree Structure)
```http
GET /api/items/categories?limit=1000
```
Returns flat list - frontend builds tree

### Create Category
```http
POST /api/items/categories
{
  "category_name": "ORGANIC COTTON",
  "category_code": "ORGC",
  "parent_category_id": "COTT",  // optional
  "inventory_class": "raw_materials",
  "selected_uoms": ["KGS"]
}
```

### Update Category
```http
PUT /api/items/categories/{category_id}
{
  // same as create
}
```
Note: Changing `inventory_class` updates all descendants

## Troubleshooting

### Categories Not Showing
- Check `is_active` flag
- Verify `inventory_class` is set (required after migration)
- Check filters in tree view

### Cannot Create Deep Levels
- No technical limit - should work
- Check browser console for errors
- Verify parent exists and is active

### Tree Not Expanding
- Click chevron icon (▶/▼) to expand/collapse
- Or click category name to edit

## Future Enhancements

Possible additions:
- Drag-and-drop to reorganize tree
- Bulk operations (move multiple categories)
- Export tree structure to Excel/CSV
- Visual tree depth limit warning
- Category path display (breadcrumbs)

---

**Remember**: With unlimited levels comes responsibility - keep your hierarchy logical and maintainable!
