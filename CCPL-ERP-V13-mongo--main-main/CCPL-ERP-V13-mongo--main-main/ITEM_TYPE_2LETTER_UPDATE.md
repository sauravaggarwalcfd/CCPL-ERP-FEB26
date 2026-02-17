# Item Type Code Update: 4-Letter → 2-Letter

## Overview
Successfully updated all item type codes from 4-letter to 2-letter format for use in SKU generation and throughout the system.

---

## ✅ Code Mapping

| Old Code (4-letter) | New Code (2-letter) | Description |
|---------------------|---------------------|-------------|
| YARN | **YN** | Yarn & Fiber |
| GFAB | **GF** | Grey Fabric |
| DFAB | **DF** | Dyed Fabric |
| TRIM | **TR** | Trims & Accessories |
| DYCM | **DY** | Dyes & Chemicals |
| CUTP | **CP** | Cut Components |
| SEMI | **SF** | Semi-Finished Goods |
| FGDS | **FG** | Finished Goods |
| PACK | **PK** | Packaging Materials |
| CONS | **CS** | Consumables & Spares |

---

## 📁 Files Updated

### Backend:

1. **`backend/app/models/item_type.py`**
   - Updated module docstring from "4 characters" to "2 characters"
   - Updated SEED_ITEM_TYPES with 10 new 2-letter codes
   - Maintained validation: 2-4 characters (flexible)

2. **`backend/app/models/category_hierarchy.py`**
   - Updated SEED_CATEGORIES to use new 2-letter item type codes:
     - FABR: RM → **GF**
     - TRIM: AC → **TR**
     - YARN: RM → **YN**
     - CHEM: CM → **DY**
     - PACK: CM → **PK**
     - CONS: CM → **CS**

3. **`backend/migrate_item_types.py`** (New)
   - Migration script to update existing database records
   - Successfully migrated 10 item types
   - Updated category references

---

## 🔄 Migration Results

**Database Migration:**
- ✅ 10 item types updated successfully
- ✅ 0 items skipped
- ✅ Category item_type references updated
- ✅ All collections synchronized

**Collections Updated:**
- `item_types` - Main item type definitions
- `item_categories` - Category hierarchy references
- `item_sub_categories` - Sub-category references
- `item_divisions` - Division references
- `item_classes` - Class references
- `item_sub_classes` - Sub-class references

---

## 💡 New Item Type Definitions

```python
SEED_ITEM_TYPES = [
    {"type_code": "YN", "type_name": "Yarn & Fiber", ...},
    {"type_code": "GF", "type_name": "Grey Fabric", ...},
    {"type_code": "DF", "type_name": "Dyed Fabric", ...},
    {"type_code": "TR", "type_name": "Trims & Accessories", ...},
    {"type_code": "DY", "type_name": "Dyes & Chemicals", ...},
    {"type_code": "CP", "type_name": "Cut Components", ...},
    {"type_code": "SF", "type_name": "Semi-Finished Goods", ...},
    {"type_code": "FG", "type_name": "Finished Goods", ...},
    {"type_code": "PK", "type_name": "Packaging Materials", ...},
    {"type_code": "CS", "type_name": "Consumables & Spares", ...},
]
```

---

## 🎯 SKU Format Impact

### Before (with 4-letter codes):
```
YARN-CTTN-001
GFAB-PC60-002
FGDS-TSHT-003
```

### After (with 2-letter codes):
```
YN-CTTN-001
GF-PC60-002
FG-TSHT-003
```

**Benefits:**
- ✅ Shorter, more concise SKU codes
- ✅ Easier to read and remember
- ✅ More consistent with industry standards
- ✅ Reduces data entry errors
- ✅ Saves storage space

---

## 🔧 Validation Rules

**Item Type Code:**
- **Length:** 2-4 characters (flexible)
- **Format:** Alphanumeric only
- **Case:** Always uppercase
- **Uniqueness:** Must be unique across all item types

**Examples of Valid Codes:**
- ✅ YN (2 chars)
- ✅ GF (2 chars)
- ✅ FG (2 chars)
- ✅ ABCD (4 chars - still allowed for flexibility)

---

## 📊 Complete Item Type List

| Code | Name | Category | Purchase | Sale | Default UOM |
|------|------|----------|----------|------|-------------|
| **YN** | Yarn & Fiber | Raw Material | ✅ | ❌ | KG |
| **GF** | Grey Fabric | Raw Material | ✅ | ❌ | MTR |
| **DF** | Dyed Fabric | Processed Material | ✅ | ❌ | MTR |
| **TR** | Trims & Accessories | Components | ✅ | ❌ | PCS |
| **DY** | Dyes & Chemicals | Consumable | ✅ | ❌ | LTR |
| **CP** | Cut Components | Work-in-Progress | ❌ | ❌ | PCS |
| **SF** | Semi-Finished Goods | Work-in-Progress | ❌ | ❌ | PCS |
| **FG** | Finished Goods | Final Product | ❌ | ✅ | PCS |
| **PK** | Packaging Materials | Consumable | ✅ | ❌ | PCS |
| **CS** | Consumables & Spares | Consumable | ✅ | ❌ | PCS |

---

## 🚀 Usage in System

### 1. **SKU Generation**
Item type code is used as the first part of SKU:
```
{ITEM_TYPE}-{CATEGORY}-{SEQUENCE}
Example: FG-APRL-0001
```

### 2. **Category Assignment**
Each category is linked to a default item type:
```javascript
APRL (Apparel) → FG (Finished Goods)
FABR (Fabrics) → GF (Grey Fabric)
YARN (Yarns) → YN (Yarn & Fiber)
```

### 3. **Inventory Tracking**
Item type determines:
- Purchase vs Sale permissions
- Quality check requirements
- Default UOM
- Stock tracking behavior

---

## 🔍 How to Verify

### Check in UI:
1. Navigate to Item Types page
2. All codes should show 2 letters
3. SKU generation should use 2-letter prefixes

### Check via API:
```bash
# List all item types
curl http://localhost:8000/api/item-types

# Expected response:
[
  {"type_code": "YN", "type_name": "Yarn & Fiber", ...},
  {"type_code": "GF", "type_name": "Grey Fabric", ...},
  ...
]
```

### Check Database:
```javascript
db.item_types.find({}, {type_code: 1, type_name: 1})

// Should return 2-letter codes only
{ "type_code": "YN", "type_name": "Yarn & Fiber" }
{ "type_code": "GF", "type_name": "Grey Fabric" }
...
```

---

## 📝 Migration Log

**Date:** 2025-12-18
**Time:** 12:11 UTC
**Status:** ✅ Completed Successfully

**Actions Performed:**
1. ✅ Updated item_type.py model and seed data
2. ✅ Updated category_hierarchy.py seed data
3. ✅ Ran database migration script
4. ✅ Updated 10 item type records
5. ✅ Updated category references
6. ✅ Restarted backend service

**Records Updated:**
- Item Types: 10 updated
- Categories: References updated
- Sub-Categories: References updated
- Divisions: References updated
- Classes: References updated
- Sub-Classes: References updated

---

## ⚠️ Important Notes

1. **Backward Compatibility:** The system still accepts 2-4 character codes for flexibility
2. **Existing SKUs:** Old SKUs with 4-letter codes remain valid
3. **New Items:** All new items will use 2-letter codes
4. **Re-seeding:** Can re-seed item types anytime via API: `POST /api/item-types/seed`
5. **Migration Script:** Can be re-run safely (idempotent)

---

## 🎓 Best Practices

### When Creating New Item Types:
1. Use 2-letter codes for consistency
2. Use meaningful abbreviations
3. Avoid confusing similar codes (e.g., CS vs SC)
4. Document the meaning of each code
5. Maintain uniqueness

### When Creating SKUs:
1. Follow pattern: `{TYPE}-{CATEGORY}-{SEQ}`
2. Use 2-letter type codes
3. Keep category codes 2-4 letters
4. Use sequential numbering

---

**Last Updated:** 2025-12-18
**Backend Status:** ✅ Running
**Migration Status:** ✅ Complete
**Ready for Use:** ✅ Yes
