"""
Migration Script: Update Item Type Codes from 4-letter to 2-letter
This script updates existing item types in the database to use 2-letter codes.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB Connection
MONGODB_URL = "mongodb://mongodb:27017"  # Use 'mongodb' service name in Docker
DATABASE_NAME = "inventory_erp"

# Mapping of old 4-letter codes to new 2-letter codes
CODE_MAPPING = {
    "YARN": "YN",
    "GFAB": "GF",
    "DFAB": "DF",
    "TRIM": "TR",
    "DYCM": "DY",
    "CUTP": "CP",
    "SEMI": "SF",
    "FGDS": "FG",
    "PACK": "PK",
    "CONS": "CS",
    # Legacy codes
    "RM": "YN",  # Raw Material → Yarn
    "SG": "SF",  # Sub Goods → Semi-Finished
    "AC": "TR",  # Accessories → Trims
    "CM": "CS",  # Consumable → Consumables & Spares
}

async def migrate_item_types():
    """Migrate item type codes from 4-letter to 2-letter"""

    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    try:
        # Get item_types collection
        item_types_collection = db.item_types

        print("Starting item type code migration...")
        print(f"Mapping: {CODE_MAPPING}")
        print("-" * 60)

        updated_count = 0
        skipped_count = 0

        # Find all item types
        cursor = item_types_collection.find({})
        item_types = await cursor.to_list(length=None)

        for item_type in item_types:
            old_code = item_type.get("type_code")

            # Check if needs migration
            if old_code in CODE_MAPPING:
                new_code = CODE_MAPPING[old_code]

                # Check if new code already exists
                existing = await item_types_collection.find_one({"type_code": new_code})

                if existing:
                    print(f"⚠️  Skipping {old_code} → {new_code} (already exists)")
                    # Delete the old one
                    await item_types_collection.delete_one({"_id": item_type["_id"]})
                    skipped_count += 1
                else:
                    # Update the code
                    result = await item_types_collection.update_one(
                        {"_id": item_type["_id"]},
                        {
                            "$set": {
                                "type_code": new_code,
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )

                    if result.modified_count > 0:
                        print(f"✅ Updated: {old_code} → {new_code}")
                        updated_count += 1
            else:
                if len(old_code) > 2:
                    print(f"⚠️  Unknown code: {old_code} (length {len(old_code)})")

        print("-" * 60)
        print(f"\nMigration Complete!")
        print(f"Updated: {updated_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Total processed: {len(item_types)}")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        client.close()

async def update_category_item_types():
    """Update item_type references in category hierarchy"""

    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    try:
        print("\nUpdating item_type in category collections...")
        print("-" * 60)

        collections = [
            "item_categories",
            "item_sub_categories",
            "item_divisions",
            "item_classes",
            "item_sub_classes"
        ]

        for coll_name in collections:
            collection = db[coll_name]

            # Update RM → YN
            result = await collection.update_many(
                {"item_type": "RM"},
                {"$set": {"item_type": "YN"}}
            )
            if result.modified_count > 0:
                print(f"✅ {coll_name}: Updated {result.modified_count} records (RM → YN)")

            # Update AC → TR
            result = await collection.update_many(
                {"item_type": "AC"},
                {"$set": {"item_type": "TR"}}
            )
            if result.modified_count > 0:
                print(f"✅ {coll_name}: Updated {result.modified_count} records (AC → TR)")

            # Update CM → CS
            result = await collection.update_many(
                {"item_type": "CM"},
                {"$set": {"item_type": "CS"}}
            )
            if result.modified_count > 0:
                print(f"✅ {coll_name}: Updated {result.modified_count} records (CM → CS)")

        print("-" * 60)
        print("Category item_type migration complete!")

    except Exception as e:
        print(f"❌ Error updating categories: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    print("=" * 60)
    print("ITEM TYPE CODE MIGRATION: 4-letter → 2-letter")
    print("=" * 60)
    print()

    # Run migrations
    asyncio.run(migrate_item_types())
    asyncio.run(update_category_item_types())

    print("\n" + "=" * 60)
    print("✅ All migrations completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart the backend: docker-compose restart backend")
    print("2. Re-seed item types: POST /api/item-types/seed")
    print("3. Verify in UI that all item types show 2-letter codes")
