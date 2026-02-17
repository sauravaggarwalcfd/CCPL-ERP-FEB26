"""
Seed data script for Variant Masters
Populates initial data for Colours, Sizes, UOMs, and Variant Groups
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.colour_master import ColourMaster, ColourGroup, hex_to_rgb, COLOUR_GROUP_NAMES
from app.models.size_master import SizeMaster, SizeGroup, SIZE_GROUP_NAMES
from app.models.uom_master import UOMMaster, UOMGroup, UOM_GROUP_NAMES
from app.models.variant_groups import VariantGroup, VARIANT_GROUPS_SEED


# ==================== COLOUR SEED DATA ====================

COLOUR_SEED_DATA = [
    # Thread Colors
    {"colour_code": "THR-WHT", "colour_name": "White", "colour_hex": "#FFFFFF", "colour_group": ColourGroup.THREAD_COLORS, "display_order": 1},
    {"colour_code": "THR-BLK", "colour_name": "Black", "colour_hex": "#000000", "colour_group": ColourGroup.THREAD_COLORS, "display_order": 2},
    {"colour_code": "THR-RED", "colour_name": "Red", "colour_hex": "#DC2626", "colour_group": ColourGroup.THREAD_COLORS, "display_order": 3},
    {"colour_code": "THR-BLU", "colour_name": "Blue", "colour_hex": "#2563EB", "colour_group": ColourGroup.THREAD_COLORS, "display_order": 4},
    {"colour_code": "THR-GRN", "colour_name": "Green", "colour_hex": "#16A34A", "colour_group": ColourGroup.THREAD_COLORS, "display_order": 5},

    # Fabric Colors
    {"colour_code": "FAB-NVY", "colour_name": "Navy Blue", "colour_hex": "#1E3A8A", "colour_group": ColourGroup.FABRIC_COLORS, "display_order": 1},
    {"colour_code": "FAB-BEI", "colour_name": "Beige", "colour_hex": "#D4A574", "colour_group": ColourGroup.FABRIC_COLORS, "display_order": 2},
    {"colour_code": "FAB-GRY", "colour_name": "Grey", "colour_hex": "#6B7280", "colour_group": ColourGroup.FABRIC_COLORS, "display_order": 3},
    {"colour_code": "FAB-BRN", "colour_name": "Brown", "colour_hex": "#92400E", "colour_group": ColourGroup.FABRIC_COLORS, "display_order": 4},
    {"colour_code": "FAB-CRM", "colour_name": "Cream", "colour_hex": "#FEF3C7", "colour_group": ColourGroup.FABRIC_COLORS, "display_order": 5},

    # Button Colors
    {"colour_code": "BTN-WHT", "colour_name": "White", "colour_hex": "#FFFFFF", "colour_group": ColourGroup.BUTTON_COLORS, "display_order": 1},
    {"colour_code": "BTN-BLK", "colour_name": "Black", "colour_hex": "#000000", "colour_group": ColourGroup.BUTTON_COLORS, "display_order": 2},
    {"colour_code": "BTN-GLD", "colour_name": "Gold", "colour_hex": "#F59E0B", "colour_group": ColourGroup.BUTTON_COLORS, "display_order": 3},
    {"colour_code": "BTN-SLV", "colour_name": "Silver", "colour_hex": "#9CA3AF", "colour_group": ColourGroup.BUTTON_COLORS, "display_order": 4},

    # Label Colors
    {"colour_code": "LBL-WHT", "colour_name": "White", "colour_hex": "#FFFFFF", "colour_group": ColourGroup.LABEL_COLORS, "display_order": 1},
    {"colour_code": "LBL-BLK", "colour_name": "Black", "colour_hex": "#000000", "colour_group": ColourGroup.LABEL_COLORS, "display_order": 2},
    {"colour_code": "LBL-RED", "colour_name": "Red", "colour_hex": "#DC2626", "colour_group": ColourGroup.LABEL_COLORS, "display_order": 3},
]


# ==================== SIZE SEED DATA ====================

SIZE_SEED_DATA = [
    # Apparel Sizes
    {"size_code": "XS", "size_name": "Extra Small", "size_group": SizeGroup.APPAREL_SIZES, "display_order": 1},
    {"size_code": "S", "size_name": "Small", "size_group": SizeGroup.APPAREL_SIZES, "display_order": 2},
    {"size_code": "M", "size_name": "Medium", "size_group": SizeGroup.APPAREL_SIZES, "display_order": 3},
    {"size_code": "L", "size_name": "Large", "size_group": SizeGroup.APPAREL_SIZES, "display_order": 4},
    {"size_code": "XL", "size_name": "Extra Large", "size_group": SizeGroup.APPAREL_SIZES, "display_order": 5},
    {"size_code": "XXL", "size_name": "Double XL", "size_group": SizeGroup.APPAREL_SIZES, "display_order": 6},

    # Standard Sizes
    {"size_code": "SM", "size_name": "Small", "size_group": SizeGroup.STANDARD_SIZES, "display_order": 1},
    {"size_code": "MD", "size_name": "Medium", "size_group": SizeGroup.STANDARD_SIZES, "display_order": 2},
    {"size_code": "LG", "size_name": "Large", "size_group": SizeGroup.STANDARD_SIZES, "display_order": 3},

    # Numeric Sizes
    {"size_code": "28", "size_name": "Size 28", "size_group": SizeGroup.NUMERIC_SIZES, "numeric_value": 28, "display_order": 1},
    {"size_code": "30", "size_name": "Size 30", "size_group": SizeGroup.NUMERIC_SIZES, "numeric_value": 30, "display_order": 2},
    {"size_code": "32", "size_name": "Size 32", "size_group": SizeGroup.NUMERIC_SIZES, "numeric_value": 32, "display_order": 3},
    {"size_code": "34", "size_name": "Size 34", "size_group": SizeGroup.NUMERIC_SIZES, "numeric_value": 34, "display_order": 4},
    {"size_code": "36", "size_name": "Size 36", "size_group": SizeGroup.NUMERIC_SIZES, "numeric_value": 36, "display_order": 5},
    {"size_code": "38", "size_name": "Size 38", "size_group": SizeGroup.NUMERIC_SIZES, "numeric_value": 38, "display_order": 6},
    {"size_code": "40", "size_name": "Size 40", "size_group": SizeGroup.NUMERIC_SIZES, "numeric_value": 40, "display_order": 7},
]


# ==================== UOM SEED DATA ====================

UOM_SEED_DATA = [
    # Weight Units
    {"uom_code": "KG", "uom_name": "Kilogram", "uom_symbol": "kg", "uom_group": UOMGroup.WEIGHT, "conversion_to_base": 1.0, "is_base_uom": True, "display_order": 1},
    {"uom_code": "G", "uom_name": "Gram", "uom_symbol": "g", "uom_group": UOMGroup.WEIGHT, "conversion_to_base": 0.001, "display_order": 2},
    {"uom_code": "LB", "uom_name": "Pound", "uom_symbol": "lb", "uom_group": UOMGroup.WEIGHT, "conversion_to_base": 0.453592, "display_order": 3},
    {"uom_code": "OZ", "uom_name": "Ounce", "uom_symbol": "oz", "uom_group": UOMGroup.WEIGHT, "conversion_to_base": 0.0283495, "display_order": 4},

    # Length Units
    {"uom_code": "M", "uom_name": "Meter", "uom_symbol": "m", "uom_group": UOMGroup.LENGTH, "conversion_to_base": 1.0, "is_base_uom": True, "display_order": 1},
    {"uom_code": "CM", "uom_name": "Centimeter", "uom_symbol": "cm", "uom_group": UOMGroup.LENGTH, "conversion_to_base": 0.01, "display_order": 2},
    {"uom_code": "MM", "uom_name": "Millimeter", "uom_symbol": "mm", "uom_group": UOMGroup.LENGTH, "conversion_to_base": 0.001, "display_order": 3},
    {"uom_code": "IN", "uom_name": "Inch", "uom_symbol": "in", "uom_group": UOMGroup.LENGTH, "conversion_to_base": 0.0254, "display_order": 4},
    {"uom_code": "FT", "uom_name": "Feet", "uom_symbol": "ft", "uom_group": UOMGroup.LENGTH, "conversion_to_base": 0.3048, "display_order": 5},
    {"uom_code": "YD", "uom_name": "Yard", "uom_symbol": "yd", "uom_group": UOMGroup.LENGTH, "conversion_to_base": 0.9144, "display_order": 6},

    # Volume Units
    {"uom_code": "L", "uom_name": "Liter", "uom_symbol": "L", "uom_group": UOMGroup.VOLUME, "conversion_to_base": 1.0, "is_base_uom": True, "display_order": 1},
    {"uom_code": "ML", "uom_name": "Milliliter", "uom_symbol": "mL", "uom_group": UOMGroup.VOLUME, "conversion_to_base": 0.001, "display_order": 2},
    {"uom_code": "GAL", "uom_name": "Gallon", "uom_symbol": "gal", "uom_group": UOMGroup.VOLUME, "conversion_to_base": 3.78541, "display_order": 3},

    # Count Units
    {"uom_code": "PCS", "uom_name": "Pieces", "uom_symbol": "pcs", "uom_group": UOMGroup.COUNT, "conversion_to_base": 1.0, "is_base_uom": True, "display_order": 1},
    {"uom_code": "DZ", "uom_name": "Dozen", "uom_symbol": "dz", "uom_group": UOMGroup.COUNT, "conversion_to_base": 12.0, "display_order": 2},
    {"uom_code": "GRS", "uom_name": "Gross", "uom_symbol": "grs", "uom_group": UOMGroup.COUNT, "conversion_to_base": 144.0, "display_order": 3},
    {"uom_code": "BOX", "uom_name": "Box", "uom_symbol": "box", "uom_group": UOMGroup.COUNT, "conversion_to_base": 1.0, "display_order": 4},
    {"uom_code": "PKT", "uom_name": "Packet", "uom_symbol": "pkt", "uom_group": UOMGroup.COUNT, "conversion_to_base": 1.0, "display_order": 5},

    # Area Units
    {"uom_code": "SQM", "uom_name": "Square Meter", "uom_symbol": "m²", "uom_group": UOMGroup.AREA, "conversion_to_base": 1.0, "is_base_uom": True, "display_order": 1},
    {"uom_code": "SQFT", "uom_name": "Square Feet", "uom_symbol": "ft²", "uom_group": UOMGroup.AREA, "conversion_to_base": 0.092903, "display_order": 2},
    {"uom_code": "SQIN", "uom_name": "Square Inch", "uom_symbol": "in²", "uom_group": UOMGroup.AREA, "conversion_to_base": 0.00064516, "display_order": 3},
]


# ==================== SEED FUNCTIONS ====================

async def seed_variant_groups():
    """Seed variant group definitions"""
    print("Seeding Variant Groups...")

    existing_count = await VariantGroup.count()
    if existing_count > 0:
        print(f"  ⚠ Variant Groups already exist ({existing_count} records). Skipping.")
        return

    for group_data in VARIANT_GROUPS_SEED:
        group = VariantGroup(**group_data)
        await group.insert()

    print(f"  ✓ Created {len(VARIANT_GROUPS_SEED)} variant groups")


async def seed_colours():
    """Seed colour master data"""
    print("Seeding Colours...")

    existing_count = await ColourMaster.count()
    if existing_count > 0:
        print(f"  ⚠ Colours already exist ({existing_count} records). Skipping.")
        return

    for colour_data in COLOUR_SEED_DATA:
        # Calculate RGB from hex
        rgb = hex_to_rgb(colour_data["colour_hex"])

        # Get group name
        group_name = COLOUR_GROUP_NAMES.get(
            colour_data["colour_group"],
            colour_data["colour_group"].value
        )

        colour = ColourMaster(
            colour_code=colour_data["colour_code"],
            colour_name=colour_data["colour_name"],
            colour_hex=colour_data["colour_hex"],
            rgb_value=rgb,
            colour_group=colour_data["colour_group"],
            group_name=group_name,
            display_order=colour_data["display_order"],
        )
        await colour.insert()

    print(f"  ✓ Created {len(COLOUR_SEED_DATA)} colours")


async def seed_sizes():
    """Seed size master data"""
    print("Seeding Sizes...")

    existing_count = await SizeMaster.count()
    if existing_count > 0:
        print(f"  ⚠ Sizes already exist ({existing_count} records). Skipping.")
        return

    for size_data in SIZE_SEED_DATA:
        # Get group name
        group_name = SIZE_GROUP_NAMES.get(
            size_data["size_group"],
            size_data["size_group"].value
        )

        size = SizeMaster(
            size_code=size_data["size_code"],
            size_name=size_data["size_name"],
            size_group=size_data["size_group"],
            group_name=group_name,
            numeric_value=size_data.get("numeric_value"),
            unit="SIZE",
            display_order=size_data["display_order"],
        )
        await size.insert()

    print(f"  ✓ Created {len(SIZE_SEED_DATA)} sizes")


async def seed_uoms():
    """Seed UOM master data"""
    print("Seeding UOMs...")

    existing_count = await UOMMaster.count()
    if existing_count > 0:
        print(f"  ⚠ UOMs already exist ({existing_count} records). Skipping.")
        return

    for uom_data in UOM_SEED_DATA:
        # Get group name
        group_name = UOM_GROUP_NAMES.get(
            uom_data["uom_group"],
            uom_data["uom_group"].value
        )

        uom = UOMMaster(
            uom_code=uom_data["uom_code"],
            uom_name=uom_data["uom_name"],
            uom_symbol=uom_data["uom_symbol"],
            uom_group=uom_data["uom_group"],
            group_name=group_name,
            conversion_to_base=uom_data["conversion_to_base"],
            is_base_uom=uom_data.get("is_base_uom", False),
            display_order=uom_data["display_order"],
        )
        await uom.insert()

    print(f"  ✓ Created {len(UOM_SEED_DATA)} UOMs")


async def main():
    """Main seed function"""
    print("=" * 60)
    print("VARIANT MASTER SEED DATA")
    print("=" * 60)

    # Connect to database
    print("\nConnecting to database...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[ColourMaster, SizeMaster, UOMMaster, VariantGroup]
    )
    print("  ✓ Connected")

    # Run seed functions
    print("\n" + "=" * 60)
    await seed_variant_groups()
    print()
    await seed_colours()
    print()
    await seed_sizes()
    print()
    await seed_uoms()

    # Close connection
    print("\n" + "=" * 60)
    print("Seed completed successfully!")
    print("=" * 60)
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
