# Fix Summary: Sizes and UOMs

## Changes Implemented

### 1. Backend Model Updates (Confirmed)
*   **SizeMaster**: Verified that `SizeCreate` and `SizeUpdate` schemas accept any string for `size_group`.
*   **UOMMaster**: Verified that `UOMCreate` and `UOMUpdate` schemas accept any string for `uom_group`.

### 2. Demo Data Seeded
Added the following groups and sample items:

#### Sizes
*   **Apparel Sizes** (`APPAREL_SIZES`)
    *   XS, S, M, L, XL, XXL
*   **Numeric Sizes** (`NUMERIC_SIZES`)
    *   Size 28, Size 30, Size 32, Size 34
*   **Standard Sizes** (`STANDARD_SIZES`)

#### UOMs (Units of Measure)
*   **Weight** (`WEIGHT`)
    *   Kilogram (kg) - Base Unit
    *   Gram (g)
    *   Pound (lb)
*   **Length** (`LENGTH`)
    *   Meter (m) - Base Unit
    *   Centimeter (cm)
    *   Millimeter (mm)
    *   Inch (in)
*   **Count** (`COUNT`)
    *   Pieces (pcs) - Base Unit
    *   Dozen (doz)
    *   Box (box)

### 3. Verification
*   Verified that the API returns the correct list of groups for both Sizes and UOMs.
*   The "Input should be..." error will no longer appear for Sizes and UOMs.

## How to Test
1.  Refresh your browser.
2.  Go to **Variant Master > Sizes**.
    *   You should see the new demo sizes.
    *   Click **Add Size** and verify the group dropdown works.
3.  Go to **Variant Master > UOM**.
    *   You should see the new demo UOMs.
    *   Click **Add UOM** and verify the group dropdown works.
