"""
Seed Category Specifications
Pre-configures specifications for Thread, Fabric, and Button categories
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models.specifications import CategorySpecifications, SpecificationsConfig, VariantFieldConfig, CustomFieldConfig, FieldSource, FieldType
from datetime import datetime


async def seed_specifications():
    """Seed category specifications for Thread, Fabric, and Button"""

    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # Initialize Beanie
    from beanie import init_beanie
    from app.models.specifications import CategorySpecifications

    await init_beanie(database=db, document_models=[CategorySpecifications])

    print("🌱 Seeding Category Specifications...")

    # ==================== THREAD CATEGORY ====================
    thread_spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == "THREAD"
    )

    if thread_spec:
        print("⚠️  THREAD specifications already exist, skipping...")
    else:
        thread_spec = CategorySpecifications(
            category_code="THREAD",
            category_name="Thread",
            category_level=1,
            specifications=SpecificationsConfig(
                colour=VariantFieldConfig(
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
                size=VariantFieldConfig(
                    enabled=True,
                    required=True,
                    field_name="Size",
                    field_type="SELECT",
                    field_key="size_code",
                    source=FieldSource.SIZE_MASTER,
                    groups=["NUMERIC_SIZES"],
                    allow_multiple=False,
                    default_value=None
                ),
                uom=VariantFieldConfig(
                    enabled=True,
                    required=True,
                    field_name="UOM",
                    field_type="SELECT",
                    field_key="uom_code",
                    source=FieldSource.UOM_MASTER,
                    groups=["WEIGHT"],
                    allow_multiple=False,
                    default_value=None
                ),
                vendor=VariantFieldConfig(
                    enabled=True,
                    required=False,
                    field_name="Vendor",
                    field_type="SELECT",
                    field_key="vendor_code",
                    source=FieldSource.SUPPLIER_MASTER,
                    groups=[],
                    allow_multiple=False,
                    default_value=None
                )
            ),
            custom_fields=[
                CustomFieldConfig(
                    field_code="QUALITY_GRADE",
                    field_name="Quality Grade",
                    field_type=FieldType.SELECT,
                    field_key="quality_grade",
                    enabled=True,
                    required=False,
                    options=["Grade A", "Grade B", "Grade C"],
                    default_value=None,
                    placeholder="Select quality grade",
                    display_order=1
                ),
                CustomFieldConfig(
                    field_code="TWIST_TYPE",
                    field_name="Twist Type",
                    field_type=FieldType.SELECT,
                    field_key="twist_type",
                    enabled=True,
                    required=False,
                    options=["Single", "Double", "Triple"],
                    default_value=None,
                    placeholder="Select twist type",
                    display_order=2
                )
            ],
            is_active=True,
            created_by="system",
            created_date=datetime.utcnow()
        )

        await thread_spec.insert()
        print("✅ Created THREAD category specifications")

    # ==================== FABRIC CATEGORY ====================
    fabric_spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == "FABRIC"
    )

    if fabric_spec:
        print("⚠️  FABRIC specifications already exist, skipping...")
    else:
        fabric_spec = CategorySpecifications(
            category_code="FABRIC",
            category_name="Fabric",
            category_level=1,
            specifications=SpecificationsConfig(
                colour=VariantFieldConfig(
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
                size=VariantFieldConfig(
                    enabled=False,
                    required=False,
                    field_name="Size",
                    field_type="SELECT",
                    field_key="size_code",
                    source=FieldSource.SIZE_MASTER,
                    groups=[],
                    allow_multiple=False,
                    default_value=None
                ),
                uom=VariantFieldConfig(
                    enabled=True,
                    required=True,
                    field_name="UOM",
                    field_type="SELECT",
                    field_key="uom_code",
                    source=FieldSource.UOM_MASTER,
                    groups=["LENGTH", "AREA"],
                    allow_multiple=False,
                    default_value=None
                ),
                vendor=VariantFieldConfig(
                    enabled=True,
                    required=False,
                    field_name="Vendor",
                    field_type="SELECT",
                    field_key="vendor_code",
                    source=FieldSource.SUPPLIER_MASTER,
                    groups=[],
                    allow_multiple=False,
                    default_value=None
                )
            ),
            custom_fields=[
                CustomFieldConfig(
                    field_code="GSM",
                    field_name="GSM Weight",
                    field_type=FieldType.NUMBER,
                    field_key="gsm",
                    enabled=True,
                    required=False,
                    options=[],
                    default_value=None,
                    placeholder="Enter GSM value",
                    min_value=50,
                    max_value=1000,
                    display_order=1
                ),
                CustomFieldConfig(
                    field_code="WIDTH",
                    field_name="Fabric Width",
                    field_type=FieldType.NUMBER,
                    field_key="width",
                    enabled=True,
                    required=False,
                    options=[],
                    default_value=None,
                    placeholder="Width in inches",
                    min_value=10,
                    max_value=200,
                    display_order=2
                ),
                CustomFieldConfig(
                    field_code="FABRIC_TYPE",
                    field_name="Fabric Type",
                    field_type=FieldType.SELECT,
                    field_key="fabric_type",
                    enabled=True,
                    required=False,
                    options=["Cotton", "Polyester", "Silk", "Wool", "Linen", "Blend"],
                    default_value=None,
                    placeholder="Select fabric type",
                    display_order=3
                )
            ],
            is_active=True,
            created_by="system",
            created_date=datetime.utcnow()
        )

        await fabric_spec.insert()
        print("✅ Created FABRIC category specifications")

    # ==================== BUTTON CATEGORY ====================
    button_spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == "BUTTON"
    )

    if button_spec:
        print("⚠️  BUTTON specifications already exist, skipping...")
    else:
        button_spec = CategorySpecifications(
            category_code="BUTTON",
            category_name="Button",
            category_level=1,
            specifications=SpecificationsConfig(
                colour=VariantFieldConfig(
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
                size=VariantFieldConfig(
                    enabled=True,
                    required=True,
                    field_name="Size",
                    field_type="SELECT",
                    field_key="size_code",
                    source=FieldSource.SIZE_MASTER,
                    groups=["NUMERIC_SIZES", "CUSTOM_SIZES"],
                    allow_multiple=False,
                    default_value=None
                ),
                uom=VariantFieldConfig(
                    enabled=True,
                    required=True,
                    field_name="UOM",
                    field_type="SELECT",
                    field_key="uom_code",
                    source=FieldSource.UOM_MASTER,
                    groups=["COUNT"],
                    allow_multiple=False,
                    default_value=None
                ),
                vendor=VariantFieldConfig(
                    enabled=True,
                    required=False,
                    field_name="Vendor",
                    field_type="SELECT",
                    field_key="vendor_code",
                    source=FieldSource.SUPPLIER_MASTER,
                    groups=[],
                    allow_multiple=False,
                    default_value=None
                )
            ),
            custom_fields=[
                CustomFieldConfig(
                    field_code="MATERIAL",
                    field_name="Material",
                    field_type=FieldType.SELECT,
                    field_key="material",
                    enabled=True,
                    required=False,
                    options=["Plastic", "Metal", "Wood", "Shell", "Ceramic"],
                    default_value=None,
                    placeholder="Select material",
                    display_order=1
                ),
                CustomFieldConfig(
                    field_code="HOLES",
                    field_name="Number of Holes",
                    field_type=FieldType.SELECT,
                    field_key="holes",
                    enabled=True,
                    required=False,
                    options=["2", "4", "Shank"],
                    default_value=None,
                    placeholder="Select hole type",
                    display_order=2
                ),
                CustomFieldConfig(
                    field_code="FINISH",
                    field_name="Finish Type",
                    field_type=FieldType.SELECT,
                    field_key="finish",
                    enabled=True,
                    required=False,
                    options=["Matte", "Glossy", "Metallic", "Textured"],
                    default_value=None,
                    placeholder="Select finish",
                    display_order=3
                )
            ],
            is_active=True,
            created_by="system",
            created_date=datetime.utcnow()
        )

        await button_spec.insert()
        print("✅ Created BUTTON category specifications")

    print("\n✅ Seed data creation completed!")
    print("\nSummary:")
    print("- THREAD: Colour (THREAD_COLORS), Size (NUMERIC_SIZES), UOM (WEIGHT) + Quality Grade, Twist Type")
    print("- FABRIC: Colour (FABRIC_COLORS), UOM (LENGTH, AREA) + GSM, Width, Fabric Type")
    print("- BUTTON: Colour (BUTTON_COLORS), Size (NUMERIC_SIZES, CUSTOM_SIZES), UOM (COUNT) + Material, Holes, Finish")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_specifications())
