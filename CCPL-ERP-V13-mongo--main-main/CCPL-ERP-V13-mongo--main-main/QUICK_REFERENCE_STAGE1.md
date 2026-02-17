# 📋 Stage 1 - Quick Reference Card

## System Status
🟢 **Backend**: Running on http://127.0.0.1:8000  
🟢 **Frontend**: Running on http://localhost:5173  
🟢 **Database**: MongoDB connected  
✅ **Stage 1**: COMPLETE & OPERATIONAL

---

## Access Information
**URL**: http://localhost:5173/item-category-enhanced  
**Login**: demo@example.com  
**Password**: Demo123!

---

## Navigation
1. Login to system
2. Sidebar → **Masters** → **Item Category (Enhanced)**

---

## Quick Actions

### Create Category
1. Click **"Add Category"** button
2. Fill required fields (Name, Code)
3. Select Parent (for L2/L3)
4. Choose Inventory Class & UOM
5. Fill optional details
6. Click **"Create Category"**

### View Category
- Click **👁️ Eye icon** in Actions column
- Read-only modal with all details

### Edit Category
- Click **✏️ Edit icon** in Actions column
- Modify fields (except code)
- Click **"Update Category"**

### Delete Category
- Click **🗑️ Trash icon** in Actions column
- Confirm deletion

### Search
- Type in search box for real-time filtering
- Searches Name and Code fields

### Filter by Level
- Click tabs: **All**, **Level 1**, **Level 2**, **Level 3**

---

## Form Tabs

### 1. Basic Info
- Category Code* (required, unique)
- Category Name* (required)
- Description
- Parent Category
- Level (auto-calculated)
- Sort Order

### 2. Inventory Details
- Inventory Class (RAW_MATERIALS, etc.)
- Default UOM (METER, KG, etc.)
- Waste Percentage (0-100%)
- Reorder Point
- Lead Time (days)
- ☑ Batch Tracking
- ☑ Expiry Tracking
- ☑ Quality Check Required

### 3. Cost & Supplier
- Standard Cost
- Preferred Supplier ID
- Preferred Supplier Name

### 4. Quality & Storage
- Storage Requirements (text)
- Handling Instructions (text)

---

## Inventory Classes
- `RAW_MATERIALS` - Raw materials
- `SEMI_FINISHED` - Semi-finished goods
- `FINISHED_GOODS` - Finished products
- `ACCESSORIES` - Accessories & trims
- `PACKAGING` - Packaging materials

---

## Units of Measure
- `METER` - For fabrics, ribbons
- `KG` - For yarn, chemicals
- `PIECE` - For buttons, zippers
- `YARD` - Alternative to meter
- `LITER` - For liquids
- `GRAM` - For small quantities
- `DOZEN` - For grouped items
- `SET` - For item sets

---

## Level Badges
- 🟣 **L1** - Purple - Top level (Inventory Class)
- 🔵 **L2** - Blue - Material Type
- 🟢 **L3** - Green - Sub-Category

---

## Example Hierarchy

```
RM (L1)
└── RM-FAB (L2)
    └── RM-FAB-COT (L3)
```

### Level 1: RM - Raw Materials
- Code: `RM`
- Class: RAW_MATERIALS
- Parent: None

### Level 2: RM-FAB - Fabrics
- Code: `RM-FAB`
- Class: RAW_MATERIALS
- UOM: METER
- Parent: RM

### Level 3: RM-FAB-COT - Cotton Fabrics
- Code: `RM-FAB-COT`
- Class: RAW_MATERIALS
- UOM: METER
- Parent: RM-FAB
- Waste: 5%
- Lead Time: 15 days
- Cost: 250.00

---

## Summary Cards
- **Level 1**: Count of top-level categories
- **Level 2**: Count of material types
- **Level 3**: Count of sub-categories
- **Total**: All categories

---

## API Endpoints

### Categories
- `GET /api/items/categories?limit=100` - List all
- `GET /api/items/categories/{id}` - Get one
- `POST /api/items/categories` - Create
- `PUT /api/items/categories/{id}` - Update
- `DELETE /api/items/categories/{id}` - Delete

### Helpers
- `GET /api/items/enums/inventory-classes` - Class options
- `GET /api/items/enums/units-of-measure` - UOM options
- `GET /api/items/categories/hierarchy` - Tree structure

---

## Common Issues

### ❌ "Failed to fetch categories"
✅ Check backend running on port 8000  
✅ Login again (token expired)  
✅ Check browser console

### ❌ "Cannot create category"
✅ Code must be unique  
✅ Parent must exist for L2/L3  
✅ Fill required fields (Name, Code)

### ❌ Dropdowns empty
✅ Refresh page  
✅ Check network tab (200 OK?)  
✅ Login again

### ❌ Level not calculating
✅ Select parent first  
✅ Level = parent.level + 1

---

## Validation Rules
- ✅ Code: Required, unique, max 50 chars
- ✅ Name: Required, max 200 chars
- ✅ Level: 1-3 only
- ✅ Parent: Required if level > 1
- ✅ Waste %: 0-100 if provided
- ✅ Cost: >= 0 if provided
- ✅ Code cannot be changed after creation

---

## Keyboard Shortcuts
- **Esc** - Close modal
- **Enter** - Submit form (when focused)
- **Tab** - Navigate form fields

---

## Data Entry Tips

1. **Use consistent naming**
   - Prefix codes with parent: `RM-FAB-COT`
   - Keep codes short and meaningful

2. **Fill hierarchy top-down**
   - Create L1 first
   - Then L2 children
   - Finally L3 details

3. **Use meaningful descriptions**
   - Help future users understand category
   - Include usage notes

4. **Set realistic values**
   - Waste % based on actual experience
   - Lead times from supplier data
   - Costs from purchase history

5. **Enable tracking flags wisely**
   - Batch tracking for traceability
   - Expiry for perishables
   - Quality check for critical items

---

## Documentation Files
- `QUICK_START_STAGE1.md` - Detailed testing guide
- `STAGE1_ENHANCED_CATEGORY_COMPLETE.md` - Technical docs
- `STAGE1_COMPLETE_SUMMARY.md` - Implementation summary
- `ROADMAP_7_STAGES.md` - Complete roadmap

---

## Next Stage Preview

### Stage 2: Item Master / SKU
- Auto-generate SKU codes
- Size & color variants
- Multiple suppliers
- Pricing tiers
- Image uploads
- Barcode generation

**Ready when you are!** 🚀

---

## Support Commands

### Restart Backend
```powershell
cd C:\Users\Lenovo\CCPL-ERP-V13-mongo-\backend
py -m uvicorn app.main:app --port 8000 --reload
```

### Check Servers
```powershell
# Backend
curl http://127.0.0.1:8000/docs

# Frontend
curl http://localhost:5173
```

### View Logs
- Backend: Terminal output
- Frontend: Browser console (F12)

---

**Created**: January 2025  
**Status**: ✅ OPERATIONAL  
**Version**: 1.0.0
