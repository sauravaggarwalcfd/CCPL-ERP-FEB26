import asyncio
from app.models.item import ItemCategory, ItemSubCategory, ItemMaster, InventoryType
from app.database import connect_to_mongo, close_mongo_connection
from datetime import datetime

async def setup_sample_data():
    """
    Setup sample data for Item Category hierarchy:
    Level 1: CLOTH (Clothing)
      └─ Level 2: TSHRT (T-Shirt)
           └─ Level 3: TSHRT-M-BLUE-001 (Men's Basic Crew Neck T-Shirt, Medium, Blue)
    """
    
    await connect_to_mongo()
    
    try:
        # ==================== LEVEL 1: ITEM CATEGORY ====================
        print("\n" + "="*70)
        print("SETTING UP 3-TIER ITEM HIERARCHY")
        print("="*70)
        
        # Check if category exists
        category = await ItemCategory.find_one(ItemCategory.category_id == "CLOTH")
        if not category:
            print("\n[1] Creating Item Category: CLOTH (Clothing)...")
            category = ItemCategory(
                category_id="CLOTH",
                category_name="Clothing",
                category_code="CLOTH",
                description="Apparel and clothing items",
                is_active=True
            )
            await category.save()
            print("    ✓ Category created: CLOTH")
        else:
            print("\n[1] Item Category 'CLOTH' already exists")
        
        # ==================== LEVEL 2: ITEM SUB-CATEGORY ====================
        print("\n[2] Creating Item Sub-Category: TSHRT (T-Shirt)...")
        
        sub_category = await ItemSubCategory.find_one(
            ItemSubCategory.sub_category_id == "TSHRT"
        )
        if not sub_category:
            sub_category = ItemSubCategory(
                sub_category_id="TSHRT",
                sub_category_name="T-Shirt",
                sub_category_code="TSHRT",
                category_id="CLOTH",
                category_name="Clothing",
                description="Casual and basic T-shirts",
                is_active=True
            )
            await sub_category.save()
            print("    ✓ Sub-Category created: TSHRT under CLOTH")
        else:
            print("    ✓ Sub-Category 'TSHRT' already exists")
        
        # ==================== LEVEL 3: ITEM MASTER ====================
        print("\n[3] Creating Item Master record...")
        print("    Item Code: TSHRT-M-BLUE-001")
        print("    Item Name: Men's Basic Crew Neck T-Shirt - Blue (Medium)")
        
        item = await ItemMaster.find_one(ItemMaster.item_code == "TSHRT-M-BLUE-001")
        if not item:
            item = ItemMaster(
                item_code="TSHRT-M-BLUE-001",
                item_name="Men's Basic Crew Neck T-Shirt - Blue (Medium)",
                item_description="High-quality basic crew neck t-shirt for men, made from 100% cotton with comfortable fit in Medium size, available in Blue color.",
                
                # 3-Tier Hierarchy Links
                category_id="CLOTH",
                category_name="Clothing",
                sub_category_id="TSHRT",
                sub_category_name="T-Shirt",
                
                # Attributes
                color_id="BLUE",
                color_name="Blue",
                size_id="M",
                size_name="Medium",
                brand_id=None,
                brand_name=None,
                
                # UOM and Inventory
                uom="PCS",
                inventory_type=InventoryType.STOCKED,
                
                # Pricing
                cost_price=150.00,
                selling_price=299.00,
                mrp=399.00,
                
                # Tax
                hsn_code="6109.10.00",
                gst_rate=5.0,
                
                # Warehouse Details
                warehouse_id=None,
                warehouse_name=None,
                bin_location=None,
                
                # Stock Levels
                min_stock_level=10,
                max_stock_level=500,
                reorder_point=50,
                reorder_quantity=100,
                current_stock=0,
                
                # Additional Details
                material="100% Cotton",
                weight=150.0,  # grams
                care_instructions="Machine wash cold with similar colors. Tumble dry low. Do not bleach.",
                barcode="8901234567890",
                serial_tracked=False,
                batch_tracked=True,
                
                # Status
                is_active=True,
                discontinued=False,
            )
            await item.save()
            print("\n    ✓ Item Master record created successfully!")
        else:
            print("\n    ✓ Item Master record 'TSHRT-M-BLUE-001' already exists")
        
        # ==================== SUMMARY ====================
        print("\n" + "="*70)
        print("HIERARCHY STRUCTURE CREATED")
        print("="*70)
        print("\nLevel 1 - Item Category:")
        print(f"  ID: CLOTH")
        print(f"  Name: {category.category_name}")
        
        print("\nLevel 2 - Item Sub-Category:")
        print(f"  ID: TSHRT")
        print(f"  Name: {sub_category.sub_category_name}")
        print(f"  Parent: {sub_category.category_id} ({sub_category.category_name})")
        
        print("\nLevel 3 - Item Master:")
        print(f"  Code: {item.item_code}")
        print(f"  Name: {item.item_name}")
        print(f"  Category: {item.category_id} ({item.category_name})")
        print(f"  Sub-Category: {item.sub_category_id} ({item.sub_category_name})")
        print(f"  Color: {item.color_name}")
        print(f"  Size: {item.size_name}")
        print(f"  UOM: {item.uom}")
        print(f"  Inventory Type: {item.inventory_type.value}")
        print(f"  Cost: ₹{item.cost_price:.2f}")
        print(f"  Selling Price: ₹{item.selling_price:.2f}")
        print(f"  MRP: ₹{item.mrp:.2f}")
        print(f"  Material: {item.material}")
        print(f"  Weight: {item.weight}g")
        print(f"  Status: {'Active' if item.is_active else 'Inactive'}")
        
        print("\n" + "="*70)
        print("✓ SAMPLE DATA SETUP COMPLETE!")
        print("="*70)
        print("\nYou can now use these APIs:")
        print("  GET  /api/items/categories")
        print("  GET  /api/items/categories/CLOTH")
        print("  GET  /api/items/sub-categories?category_id=CLOTH")
        print("  GET  /api/items/items")
        print("  GET  /api/items/items/TSHRT-M-BLUE-001")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(setup_sample_data())
