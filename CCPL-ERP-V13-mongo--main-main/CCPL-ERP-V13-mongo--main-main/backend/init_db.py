"""
Initialize sample data for testing
Run this once to populate the database with sample data
"""

import asyncio
from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User, EmbeddedRole
from app.models.warehouse import Warehouse
from app.models.supplier import Supplier, BankDetails
from app.models.customer import Customer
from app.models.role import Role
from app.core.security import get_password_hash
from datetime import datetime


async def init_data():
    await connect_to_mongo()
    
    try:
        # Create Admin Role
        admin_role = await Role.find_one(Role.slug == "admin")
        if not admin_role:
            admin_role = Role(
                name="Admin",
                slug="admin",
                description="Administrator with full access",
                level=1,
                permissions=["*"],
                is_active=True,
            )
            await admin_role.insert()
            print("✓ Admin role created")
        
        # Create Admin User
        admin_user = await User.find_one(User.email == "admin@inventoryerp.com")
        if not admin_user:
            admin_user = User(
                email="admin@inventoryerp.com",
                full_name="System Administrator",
                password_hash=get_password_hash("Admin@123"),
                role=EmbeddedRole(
                    id=str(admin_role.id),
                    name=admin_role.name,
                    slug=admin_role.slug,
                    level=admin_role.level
                ),
                status="active",
            )
            await admin_user.insert()
            print("✓ Admin user created (Email: admin@inventoryerp.com, Password: Admin@123)")
        
        # Create Warehouse
        warehouse = await Warehouse.find_one(Warehouse.code == "WH-001")
        if not warehouse:
            warehouse = Warehouse(
                code="WH-001",
                name="Main Warehouse",
                location="Warehouse District",
                address={
                    "line1": "123 Warehouse Street",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001",
                    "country": "India"
                },
                is_active=True,
            )
            await warehouse.insert()
            print("✓ Sample warehouse created")
        
        # Create Sample Supplier
        supplier = await Supplier.find_one(Supplier.code == "SUP-001")
        if not supplier:
            supplier = Supplier(
                code="SUP-001",
                company_name="Sample Supplier Inc.",
                contact_person="John Smith",
                email="supplier@example.com",
                phone="+91-9876543210",
                gst_number="18AABCT1234H1Z0",
                address={
                    "line1": "456 Supplier Road",
                    "city": "Delhi",
                    "state": "Delhi",
                    "pincode": "110001",
                    "country": "India"
                },
                bank_details=BankDetails(
                    bank_name="Sample Bank",
                    account_number="123456789",
                    ifsc_code="SAMP0001",
                    account_type="Current"
                ),
                is_active=True,
            )
            await supplier.insert()
            print("✓ Sample supplier created")
        
        # Create Sample Customer
        customer = await Customer.find_one(Customer.phone == "+91-9111111111")
        if not customer:
            customer = Customer(
                code="CUST-001",
                customer_type="wholesale",
                name="Sample Wholesale Customer",
                email="customer@example.com",
                phone="+91-9111111111",
                gst_number="18AABCT5678H1Z0",
                addresses=[
                    {
                        "type": "shipping",
                        "line1": "789 Customer Avenue",
                        "city": "Bangalore",
                        "state": "Karnataka",
                        "pincode": "560001",
                        "is_default": True
                    }
                ],
                is_active=True,
            )
            await customer.insert()
            print("✓ Sample customer created")
        
        print("\n✓ Database initialization complete!")
        print("\nDefault Login Credentials:")
        print("  Email: admin@inventoryerp.com")
        print("  Password: Admin@123")
        
    except Exception as e:
        print(f"✗ Error during initialization: {e}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(init_data())
