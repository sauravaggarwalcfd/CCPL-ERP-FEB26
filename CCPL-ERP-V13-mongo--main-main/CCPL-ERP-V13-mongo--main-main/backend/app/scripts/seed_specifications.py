"""
Seed data script for Specifications
Populates initial specification configurations for common categories
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.specifications import (
    CategorySpecifications,
    ItemSpecifications,
    SpecificationsConfig,
    VariantFieldConfig,
    CustomFieldConfig,
    FieldSource,
    FieldType
)


# ==================== SPECIFICATIONS SEED DATA ====================

SPECIFICATIONS_SEED_DATA = [
    # Thread Category
    {
        "category_code": "THREAD",
        "category_name": "Threads",
        "category_level": 1,
        "specifications": {
            "colour": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Colour",
                field_type="SELECT",
                field_key="colour_code",
                source=FieldSource.COLOUR_MASTER,
                groups=["THREAD_COLORS"],
                allow_multiple=False,
                default_value=None
            ),
            "size": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Thread Size",
                field_type="SELECT",
                field_key="size_code",
                source=FieldSource.SIZE_MASTER,
                groups=["NUMERIC_SIZES"],
                allow_multiple=False,
                default_value=None
            ),
            "uom": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Unit of Measure",
                field_type="SELECT",
                field_key="uom_code",
                source=FieldSource.UOM_MASTER,
                groups=["WEIGHT", "COUNT"],
                allow_multiple=False,
                default_value="KG"
            ),
            "vendor": VariantFieldConfig(
                enabled=True,
                required=False,
                field_name="Brand/Vendor",
                field_type="SELECT",
                field_key="vendor_code",
                source=FieldSource.SUPPLIER_MASTER,
                groups=[],
                allow_multiple=False,
                default_value=None
            )
        },
        "custom_fields": [
            CustomFieldConfig(
                field_code="QUALITY_GRADE",
                field_name="Quality Grade",
                field_type=FieldType.SELECT,
                field_key="quality_grade",
                enabled=True,
                required=False,
                options=["Grade A", "Grade B", "Grade C"],
                default_value="Grade A",
                display_order=1
            ),
            CustomFieldConfig(
                field_code="TWIST_TYPE",
                field_name="Twist Type",
                field_type=FieldType.SELECT,
                field_key="twist_type",
                enabled=True,
                required=True,
                options=["Single Ply", "Double Ply", "Triple Ply"],
                default_value=None,
                display_order=2
            ),
            CustomFieldConfig(
                field_code="STRENGTH",
                field_name="Strength",
                field_type=FieldType.TEXT,
                field_key="strength",
                enabled=True,
                required=False,
                options=[],
                default_value=None,
                placeholder="e.g., High, Medium, Low",
                display_order=3
            )
        ]
    },

    # Fabric Category
    {
        "category_code": "FABRIC",
        "category_name": "Fabrics",
        "category_level": 1,
        "specifications": {
            "colour": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Colour",
                field_type="SELECT",
                field_key="colour_code",
                source=FieldSource.COLOUR_MASTER,
                groups=["FABRIC_COLORS"],
                allow_multiple=False,
                default_value=None
            ),
            "size": VariantFieldConfig(
                enabled=False,  # Fabrics not sized
                required=False,
                field_name="Size",
                field_type="SELECT",
                field_key="size_code",
                source=FieldSource.SIZE_MASTER,
                groups=[],
                allow_multiple=False,
                default_value=None
            ),
            "uom": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Unit of Measure",
                field_type="SELECT",
                field_key="uom_code",
                source=FieldSource.UOM_MASTER,
                groups=["LENGTH"],
                allow_multiple=False,
                default_value="M"
            ),
            "vendor": VariantFieldConfig(
                enabled=True,
                required=False,
                field_name="Supplier",
                field_type="SELECT",
                field_key="vendor_code",
                source=FieldSource.SUPPLIER_MASTER,
                groups=[],
                allow_multiple=False,
                default_value=None
            )
        },
        "custom_fields": [
            CustomFieldConfig(
                field_code="GSM",
                field_name="GSM (Grams per Square Meter)",
                field_type=FieldType.NUMBER,
                field_key="gsm",
                enabled=True,
                required=True,
                options=[],
                default_value=None,
                placeholder="e.g., 200",
                min_value=50,
                max_value=1000,
                display_order=1
            ),
            CustomFieldConfig(
                field_code="WEAVE_TYPE",
                field_name="Weave Type",
                field_type=FieldType.SELECT,
                field_key="weave_type",
                enabled=True,
                required=True,
                options=["Cotton", "Blend", "Synthetic", "Linen", "Silk", "Wool"],
                default_value=None,
                display_order=2
            ),
            CustomFieldConfig(
                field_code="WIDTH",
                field_name="Width (inches)",
                field_type=FieldType.NUMBER,
                field_key="width",
                enabled=True,
                required=False,
                options=[],
                default_value=None,
                placeholder="e.g., 44, 58",
                min_value=20,
                max_value=120,
                display_order=3
            ),
            CustomFieldConfig(
                field_code="SHRINKAGE",
                field_name="Shrinkage %",
                field_type=FieldType.NUMBER,
                field_key="shrinkage",
                enabled=True,
                required=False,
                options=[],
                default_value=None,
                placeholder="e.g., 3, 5",
                min_value=0,
                max_value=20,
                display_order=4
            )
        ]
    },

    # Button Category
    {
        "category_code": "BUTTON",
        "category_name": "Buttons",
        "category_level": 1,
        "specifications": {
            "colour": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Colour",
                field_type="SELECT",
                field_key="colour_code",
                source=FieldSource.COLOUR_MASTER,
                groups=["BUTTON_COLORS"],
                allow_multiple=False,
                default_value=None
            ),
            "size": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Size (mm)",
                field_type="SELECT",
                field_key="size_code",
                source=FieldSource.SIZE_MASTER,
                groups=["NUMERIC_SIZES"],
                allow_multiple=False,
                default_value=None
            ),
            "uom": VariantFieldConfig(
                enabled=False,  # Buttons not measured by UOM
                required=False,
                field_name="Unit of Measure",
                field_type="SELECT",
                field_key="uom_code",
                source=FieldSource.UOM_MASTER,
                groups=[],
                allow_multiple=False,
                default_value=None
            ),
            "vendor": VariantFieldConfig(
                enabled=True,
                required=False,
                field_name="Supplier",
                field_type="SELECT",
                field_key="vendor_code",
                source=FieldSource.SUPPLIER_MASTER,
                groups=[],
                allow_multiple=False,
                default_value=None
            )
        },
        "custom_fields": [
            CustomFieldConfig(
                field_code="MATERIAL",
                field_name="Material",
                field_type=FieldType.SELECT,
                field_key="material",
                enabled=True,
                required=True,
                options=["Plastic", "Metal", "Wood", "Natural", "Resin", "Fabric"],
                default_value=None,
                display_order=1
            ),
            CustomFieldConfig(
                field_code="FINISH",
                field_name="Finish",
                field_type=FieldType.SELECT,
                field_key="finish",
                enabled=True,
                required=False,
                options=["Glossy", "Matte", "Textured", "Polished", "Brushed"],
                default_value=None,
                display_order=2
            ),
            CustomFieldConfig(
                field_code="HOLES",
                field_name="Number of Holes",
                field_type=FieldType.NUMBER,
                field_key="holes",
                enabled=True,
                required=False,
                options=[],
                default_value=2,
                min_value=0,
                max_value=6,
                display_order=3
            )
        ]
    },

    # Label Category
    {
        "category_code": "LABEL",
        "category_name": "Labels",
        "category_level": 1,
        "specifications": {
            "colour": VariantFieldConfig(
                enabled=False,  # Labels come pre-printed
                required=False,
                field_name="Colour",
                field_type="SELECT",
                field_key="colour_code",
                source=FieldSource.COLOUR_MASTER,
                groups=[],
                allow_multiple=False,
                default_value=None
            ),
            "size": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Size",
                field_type="SELECT",
                field_key="size_code",
                source=FieldSource.SIZE_MASTER,
                groups=["CUSTOM_SIZES"],
                allow_multiple=False,
                default_value=None
            ),
            "uom": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Unit of Measure",
                field_type="SELECT",
                field_key="uom_code",
                source=FieldSource.UOM_MASTER,
                groups=["COUNT"],
                allow_multiple=False,
                default_value="PCS"
            ),
            "vendor": VariantFieldConfig(
                enabled=True,
                required=False,
                field_name="Supplier",
                field_type="SELECT",
                field_key="vendor_code",
                source=FieldSource.SUPPLIER_MASTER,
                groups=[],
                allow_multiple=False,
                default_value=None
            )
        },
        "custom_fields": [
            CustomFieldConfig(
                field_code="LABEL_TYPE",
                field_name="Label Type",
                field_type=FieldType.SELECT,
                field_key="label_type",
                enabled=True,
                required=True,
                options=["Woven", "Printed", "Heat Transfer", "Embroidered", "Care Label", "Size Label"],
                default_value=None,
                display_order=1
            ),
            CustomFieldConfig(
                field_code="MATERIAL",
                field_name="Material",
                field_type=FieldType.SELECT,
                field_key="material",
                enabled=True,
                required=False,
                options=["Satin", "Cotton", "Polyester", "Taffeta", "Paper", "Leather"],
                default_value=None,
                display_order=2
            ),
            CustomFieldConfig(
                field_code="FOLD_TYPE",
                field_name="Fold Type",
                field_type=FieldType.SELECT,
                field_key="fold_type",
                enabled=True,
                required=False,
                options=["Center Fold", "End Fold", "Loop Fold", "Straight Cut", "Mitre Fold"],
                default_value=None,
                display_order=3
            )
        ]
    },

    # Zipper Category
    {
        "category_code": "ZIPPER",
        "category_name": "Zippers",
        "category_level": 1,
        "specifications": {
            "colour": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Colour",
                field_type="SELECT",
                field_key="colour_code",
                source=FieldSource.COLOUR_MASTER,
                groups=["OTHER"],
                allow_multiple=False,
                default_value=None
            ),
            "size": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Length",
                field_type="SELECT",
                field_key="size_code",
                source=FieldSource.SIZE_MASTER,
                groups=["NUMERIC_SIZES"],
                allow_multiple=False,
                default_value=None
            ),
            "uom": VariantFieldConfig(
                enabled=True,
                required=True,
                field_name="Unit of Measure",
                field_type="SELECT",
                field_key="uom_code",
                source=FieldSource.UOM_MASTER,
                groups=["LENGTH"],
                allow_multiple=False,
                default_value="CM"
            ),
            "vendor": VariantFieldConfig(
                enabled=True,
                required=False,
                field_name="Brand",
                field_type="SELECT",
                field_key="vendor_code",
                source=FieldSource.SUPPLIER_MASTER,
                groups=[],
                allow_multiple=False,
                default_value=None
            )
        },
        "custom_fields": [
            CustomFieldConfig(
                field_code="ZIPPER_TYPE",
                field_name="Zipper Type",
                field_type=FieldType.SELECT,
                field_key="zipper_type",
                enabled=True,
                required=True,
                options=["Metal", "Plastic", "Nylon Coil", "Invisible", "Open End", "Closed End"],
                default_value=None,
                display_order=1
            ),
            CustomFieldConfig(
                field_code="TEETH_SIZE",
                field_name="Teeth Size (#)",
                field_type=FieldType.SELECT,
                field_key="teeth_size",
                enabled=True,
                required=False,
                options=["#3", "#5", "#8", "#10"],
                default_value=None,
                display_order=2
            )
        ]
    }
]


# ==================== SEED FUNCTIONS ====================

async def seed_specifications():
    """Seed specification configurations"""
    print("Seeding Specifications...")

    existing_count = await CategorySpecifications.count()
    if existing_count > 0:
        print(f"  ⚠ Specifications already exist ({existing_count} records). Skipping.")
        return

    for spec_data in SPECIFICATIONS_SEED_DATA:
        # Create specifications config
        spec_config = SpecificationsConfig(
            colour=spec_data["specifications"]["colour"],
            size=spec_data["specifications"]["size"],
            uom=spec_data["specifications"]["uom"],
            vendor=spec_data["specifications"]["vendor"]
        )

        spec = CategorySpecifications(
            category_code=spec_data["category_code"],
            category_name=spec_data["category_name"],
            category_level=spec_data["category_level"],
            specifications=spec_config,
            custom_fields=spec_data["custom_fields"]
        )

        await spec.insert()
        print(f"  ✓ Created specification config for: {spec_data['category_name']}")

    print(f"  ✓ Created {len(SPECIFICATIONS_SEED_DATA)} specification configurations")


async def main():
    """Main seed function"""
    print("=" * 60)
    print("SPECIFICATIONS SEED DATA")
    print("=" * 60)

    # Connect to database
    print("\nConnecting to database...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[CategorySpecifications, ItemSpecifications]
    )
    print("  ✓ Connected")

    # Run seed functions
    print("\n" + "=" * 60)
    await seed_specifications()

    # Close connection
    print("\n" + "=" * 60)
    print("Seed completed successfully!")
    print("=" * 60)
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
