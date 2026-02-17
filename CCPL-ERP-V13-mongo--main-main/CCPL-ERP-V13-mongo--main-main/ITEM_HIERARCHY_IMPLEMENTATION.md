# 3-Tier Item Master Hierarchy Implementation

## ✅ Implementation Complete

A comprehensive 3-tier hierarchical structure for Item Master has been successfully implemented in the ERP system.

---

## 📊 Hierarchy Structure

```
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 1: ITEM CATEGORY                                    │
│  Example: CLOTH (Clothing)                                 │
│  Purpose: Broad classification of items                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├─ Unique ID: category_id
                   ├─ Name: category_name
                   ├─ Code: category_code
                   └─ Parent Category: optional (for hierarchies)
                   
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 2: ITEM SUB-CATEGORY                               │
│  Example: TSHRT (T-Shirt)                                 │
│  Purpose: Refine classification within a category         │
│  Mandatory Link: Parent category_id                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├─ Unique ID: sub_category_id
                   ├─ Name: sub_category_name
                   ├─ Code: sub_category_code
                   ├─ Parent Category: category_id (MANDATORY)
                   └─ Denormalized: category_name
                   
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 3: ITEM MASTER                                      │
│  Example: TSHRT-M-BLUE-001                                │
│  Purpose: Individual item record with full details         │
│  Mandatory Links: category_id + sub_category_id           │
└─────────────────────────────────────────────────────────────┘
                   │
                   ├─ Unique Code: item_code
                   ├─ Category: category_id (MANDATORY)
                   ├─ Sub-Category: sub_category_id (MANDATORY)
                   ├─ Attributes: color, size, brand, etc.
                   ├─ Pricing: cost, selling, MRP
                   ├─ Inventory: UOM, type, stock levels
                   └─ Metadata: created_at, updated_at
```

---

## 📋 Sample Data Created

### Level 1: Item Category
```
{
  "category_id": "CLOTH",
  "category_name": "Clothing",
  "category_code": "CLOTH",
  "description": "Apparel and clothing items",
  "is_active": true
}
```

### Level 2: Item Sub-Category
```
{
  "sub_category_id": "TSHRT",
  "sub_category_name": "T-Shirt",
  "sub_category_code": "TSHRT",
  "category_id": "CLOTH",
  "category_name": "Clothing" (denormalized),
  "description": "Casual and basic T-shirts",
  "is_active": true
}
```

### Level 3: Item Master Record
```
{
  "item_code": "TSHRT-M-BLUE-001",
  "item_name": "Men's Basic Crew Neck T-Shirt - Blue (Medium)",
  "category_id": "CLOTH",
  "category_name": "Clothing",
  "sub_category_id": "TSHRT",
  "sub_category_name": "T-Shirt",
  
  "color_id": "BLUE",
  "color_name": "Blue",
  "size_id": "M",
  "size_name": "Medium",
  
  "uom": "PCS",
  "inventory_type": "stocked",
  
  "cost_price": 150.00,
  "selling_price": 299.00,
  "mrp": 399.00,
  "gst_rate": 5.0,
  "hsn_code": "6109.10.00",
  
  "material": "100% Cotton",
  "weight": 150.0,
  "care_instructions": "Machine wash cold...",
  
  "min_stock_level": 10,
  "max_stock_level": 500,
  "reorder_point": 50,
  "reorder_quantity": 100,
  
  "is_active": true
}
```

---

## 🔒 Data Integrity Features

### 1. **Mandatory Validation**
- Item Master **requires** valid `category_id`
- Item Master **requires** valid `sub_category_id`
- Sub-Category **requires** valid parent `category_id`
- Cross-validation ensures data consistency

### 2. **Denormalization for Performance**
- Category names stored in Sub-Category records
- Category & Sub-Category names stored in Item Master records
- Reduces database joins during retrieval
- Maintains denormalized data integrity on updates

### 3. **Unique Constraints**
- Category IDs are unique globally
- Sub-Category IDs are unique globally
- Item Codes are unique globally
- Barcodes are optional but unique if provided

### 4. **Indexing**
- Fast lookup by category_id
- Fast lookup by sub_category_id
- Fast lookup by item_code
- Composite indexes for filtering queries

---

## 📡 API Endpoints

### Item Categories

**Create Item Category**
```
POST /api/items/categories
Content-Type: application/json
Authorization: Bearer <token>

{
  "category_id": "CLOTH",
  "category_name": "Clothing",
  "category_code": "CLOTH",
  "description": "Apparel and clothing items",
  "parent_category_id": null
}
```

**List Item Categories**
```
GET /api/items/categories?skip=0&limit=50&active_only=true
Authorization: Bearer <token>
```

**Get Specific Category**
```
GET /api/items/categories/{category_id}
Authorization: Bearer <token>
```

---

### Item Sub-Categories

**Create Item Sub-Category**
```
POST /api/items/sub-categories
Content-Type: application/json
Authorization: Bearer <token>

{
  "sub_category_id": "TSHRT",
  "sub_category_name": "T-Shirt",
  "sub_category_code": "TSHRT",
  "category_id": "CLOTH",
  "description": "Casual and basic T-shirts"
}
```

**List Item Sub-Categories**
```
GET /api/items/sub-categories?category_id=CLOTH&skip=0&limit=50
Authorization: Bearer <token>
```

**Get Specific Sub-Category**
```
GET /api/items/sub-categories/{sub_category_id}
Authorization: Bearer <token>
```

---

### Item Master

**Create Item Master**
```
POST /api/items/items
Content-Type: application/json
Authorization: Bearer <token>

{
  "item_code": "TSHRT-M-BLUE-001",
  "item_name": "Men's Basic Crew Neck T-Shirt - Blue (Medium)",
  "item_description": "High-quality basic crew neck t-shirt...",
  
  "category_id": "CLOTH",
  "sub_category_id": "TSHRT",
  
  "color_id": "BLUE",
  "size_id": "M",
  "brand_id": null,
  
  "uom": "PCS",
  "inventory_type": "stocked",
  
  "cost_price": 150.00,
  "selling_price": 299.00,
  "mrp": 399.00,
  
  "hsn_code": "6109.10.00",
  "gst_rate": 5.0,
  
  "min_stock_level": 10,
  "max_stock_level": 500,
  "reorder_point": 50,
  "reorder_quantity": 100,
  
  "material": "100% Cotton",
  "weight": 150.0,
  "care_instructions": "Machine wash cold...",
  "barcode": "8901234567890"
}
```

**List Item Masters**
```
GET /api/items/items?category_id=CLOTH&sub_category_id=TSHRT&skip=0&limit=50
Authorization: Bearer <token>
```

**Get Specific Item**
```
GET /api/items/items/{item_code}
Authorization: Bearer <token>
```

---

## 🗄️ Database Collections

### Collections Created:
1. **item_categories** - Master category list
2. **item_sub_categories** - Sub-categories with parent links
3. **item_master** - Individual item records with all details

### Indexes:
```
item_categories:
  - category_id (unique)
  - category_code

item_sub_categories:
  - sub_category_id (unique)
  - sub_category_code
  - category_id
  - (category_id, sub_category_id)

item_master:
  - item_code (unique)
  - category_id
  - sub_category_id
  - barcode (unique if provided)
  - (category_id, sub_category_id)
```

---

## 📝 Item Master Fields

### Identification
- `item_code` - Unique identifier (e.g., TSHRT-M-BLUE-001)
- `item_name` - Display name
- `item_description` - Detailed description

### Hierarchy Links (MANDATORY)
- `category_id` - Link to Item Category (e.g., CLOTH)
- `sub_category_id` - Link to Item Sub-Category (e.g., TSHRT)

### Attributes (Optional)
- `color_id` / `color_name` - Color reference
- `size_id` / `size_name` - Size reference
- `brand_id` / `brand_name` - Brand reference

### Inventory Settings
- `uom` - Unit of Measure (PCS, KG, LTR, MTR, etc.)
- `inventory_type` - STOCKED, NON_STOCKED, CONSUMABLE
- `warehouse_id` - Warehouse assignment
- `bin_location` - Physical location

### Stock Management
- `current_stock` - Current quantity
- `min_stock_level` - Minimum alert level
- `max_stock_level` - Maximum capacity
- `reorder_point` - Threshold for reordering
- `reorder_quantity` - Standard reorder amount

### Pricing
- `cost_price` - Purchase cost
- `selling_price` - Sale price
- `mrp` - Maximum Retail Price

### Tax & Compliance
- `hsn_code` - HSN code for tax classification
- `gst_rate` - GST rate (5%, 12%, 18%, 28%)
- `material` - Material composition
- `weight` - Weight in grams/kg

### Tracking
- `barcode` - Barcode identifier
- `serial_tracked` - Whether serial numbers required
- `batch_tracked` - Whether batch tracking required

### Status
- `is_active` - Active/Inactive status
- `discontinued` - Marked as discontinued
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

---

## ✨ Key Features

✅ **3-Tier Hierarchical Structure** - Clean separation of categories, sub-categories, and items

✅ **Mandatory Validation** - Cross-references enforced at API level

✅ **Denormalization** - Optimized for fast retrieval

✅ **Unique Constraints** - Prevents duplicate entries

✅ **Comprehensive Attributes** - Supports all ERP requirements

✅ **Pricing Management** - Cost, selling price, and MRP tracking

✅ **Inventory Control** - Stock levels, reorder points, and quantities

✅ **Tax Compliance** - HSN codes and GST rate management

✅ **Audit Trail** - Created and updated timestamps

✅ **Status Management** - Active/inactive and discontinued flags

---

## 🧪 Testing

Sample data has been created and validated:
- ✅ Item Category: CLOTH
- ✅ Item Sub-Category: TSHRT (under CLOTH)
- ✅ Item Master: TSHRT-M-BLUE-001 (under TSHRT → CLOTH)

All validations confirmed working correctly.

---

## 📚 Next Steps

1. **Extend with more categories and items** using the API endpoints
2. **Implement UI components** for Item Master management
3. **Add stock movement tracking** linked to Item Master
4. **Implement pricing rules** for different customer segments
5. **Add variant management** for color/size combinations
6. **Create reporting** on item-wise stock and sales

---

**Implementation Date**: December 13, 2025  
**Status**: ✅ Complete and Tested
