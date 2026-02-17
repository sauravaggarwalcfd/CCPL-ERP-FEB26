# Specifications Configuration - Testing Guide

## ✅ Implementation Complete!

The specifications configuration feature has been successfully implemented. This guide will help you test the complete workflow.

---

## 🎯 What Was Implemented

### Backend:
- ✅ CategorySpecifications model with variant fields and custom fields
- ✅ Complete specifications API routes
- ✅ Filtered field values endpoint (by variant group)
- ✅ Variant groups model and routes
- ✅ Seed data for THREAD, FABRIC, BUTTON categories

### Frontend:
- ✅ Specifications configuration UI in ItemCategoryMaster.jsx
- ✅ Dynamic variant field selection (Colour, Size, UOM, Vendor)
- ✅ Group filtering for each variant field
- ✅ Custom fields management
- ✅ DynamicSpecificationForm component (already existed)
- ✅ ItemCreateForm integration (already existed)

---

## 🧪 Testing the Complete Workflow

### STEP 1: Configure Specifications for a Category

1. **Navigate to Item Category Master**
   - Open the application in your browser
   - Go to "Item Category Master" page

2. **Edit an Existing Level 1 Category (e.g., THREAD)**
   - Click on a Level 1 category (like "Thread" or "Fabric")
   - Click the "Edit" button
   - Scroll down to see the **"Specifications Configuration"** section

3. **Configure Variant Fields**

   For **THREAD** category, you should see:
   - ☑️ **Colour** (enabled)
     - Groups: THREAD_COLORS selected
     - ☑️ Required

   - ☑️ **Size** (enabled)
     - Groups: NUMERIC_SIZES selected
     - ☑️ Required

   - ☑️ **UOM** (enabled)
     - Groups: WEIGHT selected
     - ☑️ Required

   - ☑️ **Vendor** (enabled)
     - No groups (all vendors available)
     - ☐ Not required

4. **View Custom Fields**

   You should see pre-configured custom fields:
   - Quality Grade (Grade A, B, C)
   - Twist Type (Single, Double, Triple)

5. **Save Changes**
   - Click "Update" to save
   - You should see a success message

### STEP 2: Create a New Category with Specifications

1. **Create a New Level 1 Category**
   - Click "Add Category" (Level 1)
   - Enter category details:
     - Code: TEST_CAT
     - Name: Test Category

2. **Configure Specifications**
   - Enable "Colour" field
     - Select groups: THREAD_COLORS
     - Check "Required"

   - Enable "Size" field
     - Select groups: NUMERIC_SIZES
     - Don't check required

3. **Add Custom Fields**
   - Click "+ Add Custom Field"
   - Enter:
     - Field Name: "Test Field"
     - Field Type: Select
   - Click "Remove" to delete if needed

4. **Save the Category**
   - Click "Create"
   - Verify success message

### STEP 3: Create an Item Using the Configured Specifications

1. **Navigate to Item Master**
   - Go to "Item Master" page
   - Click "Add Item" button

2. **Select Category**
   - Search and select your configured category (e.g., "Thread")
   - **Wait for specifications to load**

3. **Fill Specifications Section**

   You should now see a **"Specifications"** section with:

   - **Colour** dropdown
     - Should only show colors from THREAD_COLORS group
     - Should be marked as required (*)

   - **Size** dropdown
     - Should only show sizes from NUMERIC_SIZES group
     - Should be marked as required (*)

   - **UOM** dropdown
     - Should only show UOMs from WEIGHT group
     - Should be marked as required (*)

   - **Vendor** dropdown (if enabled)
     - Shows all active vendors

   - **Custom Fields**
     - Quality Grade dropdown
     - Twist Type dropdown

4. **Complete Item Creation**
   - Fill all required fields
   - Select specifications
   - Click "Save Item"
   - Verify the item is created successfully

### STEP 4: Verify Different Categories Have Different Specifications

1. **Create Item with FABRIC category**
   - Should show:
     - ✅ Colour (FABRIC_COLORS group)
     - ❌ Size (disabled for fabric)
     - ✅ UOM (LENGTH, AREA groups)
     - ✅ Custom fields: GSM, Width, Fabric Type

2. **Create Item with BUTTON category**
   - Should show:
     - ✅ Colour (BUTTON_COLORS group)
     - ✅ Size (NUMERIC_SIZES, CUSTOM_SIZES groups)
     - ✅ UOM (COUNT group)
     - ✅ Custom fields: Material, Holes, Finish

---

## 🔍 What to Verify

### Configuration Level (ItemCategoryMaster):
- [x] Specifications section only appears for Level 1 categories
- [x] Can enable/disable variant fields (Colour, Size, UOM, Vendor)
- [x] Can mark fields as required
- [x] Can select multiple groups for filtering (hold Ctrl/Cmd)
- [x] Can add/remove custom fields
- [x] Specifications are saved when category is created/updated
- [x] Specifications are loaded when editing a category

### Item Creation Level (ItemMaster):
- [x] Specifications section appears when category is selected
- [x] Only enabled fields are shown
- [x] Dropdown options are filtered by selected groups
- [x] Required fields show asterisk (*)
- [x] Custom fields appear and work correctly
- [x] Message shown if no specifications configured
- [x] Different categories show different specifications

---

## 📊 Pre-Configured Categories (Seed Data)

### THREAD Category:
```
Variant Fields:
  ☑️ Colour (THREAD_COLORS) - Required
  ☑️ Size (NUMERIC_SIZES) - Required
  ☑️ UOM (WEIGHT) - Required
  ☑️ Vendor (All vendors) - Not required

Custom Fields:
  - Quality Grade (Select: Grade A, B, C)
  - Twist Type (Select: Single, Double, Triple)
```

### FABRIC Category:
```
Variant Fields:
  ☑️ Colour (FABRIC_COLORS) - Required
  ☐ Size - Disabled
  ☑️ UOM (LENGTH, AREA) - Required
  ☑️ Vendor (All vendors) - Not required

Custom Fields:
  - GSM Weight (Number: 50-1000)
  - Fabric Width (Number: 10-200)
  - Fabric Type (Select: Cotton, Polyester, Silk, Wool, Linen, Blend)
```

### BUTTON Category:
```
Variant Fields:
  ☑️ Colour (BUTTON_COLORS) - Required
  ☑️ Size (NUMERIC_SIZES, CUSTOM_SIZES) - Required
  ☑️ UOM (COUNT) - Required
  ☑️ Vendor (All vendors) - Not required

Custom Fields:
  - Material (Select: Plastic, Metal, Wood, Shell, Ceramic)
  - Number of Holes (Select: 2, 4, Shank)
  - Finish Type (Select: Matte, Glossy, Metallic, Textured)
```

---

## 🚀 API Endpoints

You can also test the API directly:

```bash
# Get specifications for a category
curl http://localhost:8000/api/specifications/THREAD

# Get filtered field values
curl http://localhost:8000/api/specifications/THREAD/field-values/colour_code

# Get all form fields for a category
curl http://localhost:8000/api/specifications/THREAD/form-fields

# Create/Update specifications
curl -X POST http://localhost:8000/api/specifications/MY_CATEGORY \
  -H "Content-Type: application/json" \
  -d '{
    "category_name": "My Category",
    "category_level": 1,
    "specifications": {
      "colour": {
        "enabled": true,
        "required": true,
        "groups": ["THREAD_COLORS"]
      }
    },
    "custom_fields": []
  }'
```

---

## 🎉 Success Criteria

Your implementation is successful if:

1. ✅ You can configure specifications for Level 1 categories
2. ✅ Variant fields can be enabled/disabled with group filtering
3. ✅ Custom fields can be added/removed
4. ✅ Item creation form dynamically loads specifications
5. ✅ Dropdowns show filtered values based on selected groups
6. ✅ Different categories show different specifications
7. ✅ Required fields are validated
8. ✅ Pre-configured categories (Thread, Fabric, Button) work correctly

---

## 🐛 Troubleshooting

### Specifications not loading in Item Create Form:
- Check browser console for errors
- Verify category code is correct
- Ensure specifications exist for the category

### Dropdown options not filtered:
- Verify groups are selected in category configuration
- Check that master data (colours, sizes, UOMs) has the correct group assignments

### Custom fields not appearing:
- Ensure fields are marked as "enabled"
- Check field configuration in category specifications

### API errors:
- Verify backend is running on port 8000
- Check MongoDB connection
- Review backend logs for errors

---

## 📝 Notes

- Specifications configuration is **only available for Level 1 categories**
- Variant groups must exist in the system before they can be selected
- Master data (colours, sizes, UOMs) must have group assignments
- Custom fields support TEXT, NUMBER, and SELECT types
- Specifications are cached and auto-reload when category changes

---

## 🎓 Example Workflow

**Admin configures THREAD category:**
1. Enables Colour, Size, UOM, Vendor fields
2. Selects THREAD_COLORS group for colours
3. Selects NUMERIC_SIZES group for sizes
4. Adds custom fields: Quality Grade, Twist Type
5. Saves configuration

**User creates Thread item:**
1. Selects "Thread" category
2. Specifications section auto-loads
3. Sees filtered dropdowns:
   - Colours: Only thread colors (Red, Blue, Green, etc.)
   - Sizes: Only numeric sizes (30s, 40s, 50s, etc.)
   - UOMs: Only weight units (KG, GM, etc.)
4. Fills custom fields
5. Saves item

**Result:**
- Item is created with proper specifications
- Data is consistent and validated
- User only sees relevant options

---

## ✅ Testing Checklist

Copy this checklist to track your testing:

```
Configuration Testing:
[ ] Can view specifications section in ItemCategoryMaster (Level 1 only)
[ ] Can enable/disable Colour field
[ ] Can enable/disable Size field
[ ] Can enable/disable UOM field
[ ] Can enable/disable Vendor field
[ ] Can select multiple groups for each field
[ ] Can mark fields as required
[ ] Can add custom fields
[ ] Can remove custom fields
[ ] Specifications save correctly
[ ] Specifications load when editing category

Item Creation Testing:
[ ] Specifications section appears when category selected
[ ] Colour dropdown shows filtered options
[ ] Size dropdown shows filtered options
[ ] UOM dropdown shows filtered options
[ ] Vendor dropdown shows all vendors
[ ] Custom fields appear correctly
[ ] Required fields are validated
[ ] Can save item with specifications

Pre-configured Categories:
[ ] THREAD category specifications work
[ ] FABRIC category specifications work
[ ] BUTTON category specifications work

Edge Cases:
[ ] Category with no specifications configured
[ ] Category with all fields disabled
[ ] Category with only custom fields
[ ] Changing category clears previous specifications
```

---

**Happy Testing! 🎉**
