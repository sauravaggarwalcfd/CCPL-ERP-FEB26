# Dynamic Variant Groups & UI Updates

## Changes Implemented

### 1. Backend: Dynamic Group Support
Refactored the backend to support dynamic variant groups created via the `VariantGroupManager`.

*   **Models Updated**:
    *   `backend/app/models/colour_master.py`: Changed `colour_group` from `Enum` to `str`.
    *   `backend/app/models/size_master.py`: Changed `size_group` from `Enum` to `str`.
    *   `backend/app/models/uom_master.py`: Changed `uom_group` from `Enum` to `str`.

*   **Routes Updated**:
    *   `backend/app/routes/colours.py`:
        *   `get_colour_groups`: Now fetches from `VariantGroup` collection.
        *   `create_colour` / `update_colour`: Validates group against `VariantGroup` collection.
    *   `backend/app/routes/sizes.py`: Similar updates for Sizes.
    *   `backend/app/routes/uoms.py`: Similar updates for UOMs.

### 2. Frontend: UI Improvements
*   **Component Updated**: `frontend/src/components/variant-master/GroupedVariantList.jsx`
*   **Feature**: Added "Collapse/Expand" functionality for variant groups.
    *   Groups are expanded by default.
    *   Clicking the group header toggles visibility.
    *   Added chevron icons to indicate state.

## Verification
*   **New Groups**: Creating a new group in `VariantGroupManager` will now immediately make it available in the "Add Colour/Size/UOM" forms.
*   **Existing Data**: Existing data using the old Enum values will still work as long as those groups exist in the `VariantGroup` collection (which they should, if seeded).
*   **UI**: The list view now supports collapsing groups for better management of large lists.
