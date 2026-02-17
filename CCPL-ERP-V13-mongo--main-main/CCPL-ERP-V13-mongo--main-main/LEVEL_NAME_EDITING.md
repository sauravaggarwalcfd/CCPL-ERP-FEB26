# Feature Update: Inline Level Name Editing

## Changes Implemented

### 1. Inline Editing in Level Selection
*   Modified `frontend/src/pages/ItemCategoryMaster.jsx` to allow editing level names directly in the "Step 2: Select Level" list.
*   Added an edit icon (pencil) that appears on hover next to the level name.
*   Clicking the icon turns the name into an input field.
*   Changes update the `level_names` configuration for the category hierarchy.

### 2. Constraints
*   Editing is only enabled when **Level 1 (Category)** is selected.
*   This is because level names are defined at the root (Level 1) of the hierarchy and inherited by child levels.
*   To rename levels for an existing hierarchy, edit the Level 1 Category.

## How to Use
1.  Go to **Item Category Master**.
2.  Click **Create New** (or Edit an existing Level 1 Category).
3.  Select **L1 - Category**.
4.  In the "Step 2: Select Level" list, hover over any level name (e.g., "L2 - Sub-Category").
5.  Click the **pencil icon** that appears.
6.  Type the new name (e.g., "Gender") and press **Enter** or click away.
7.  The level name is updated and will be saved with the category.
