"""
Initialize database with example data
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.ip_range import IPRange
from app.models.device import Device
from app.models.user import User
from app.services.auth_service import create_admin_user_if_not_exists
from app.config import settings
import json


def init_example_data():
    """Create example network and device if they don't exist"""
    db: Session = SessionLocal()

    try:
        # Ensure admin user exists (create if needed)
        admin = create_admin_user_if_not_exists(
            db,
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD
        )
        if not admin:
            print("⚠️  Could not create or find admin user, skipping example data initialization")
            return

        # Check if example network already exists
        existing_range = db.query(IPRange).filter(IPRange.name == "Example Office Network").first()
        if existing_range:
            print("ℹ️  Example data already exists, skipping initialization")
            return

        print("📦 Creating example network and device...")

        # Create example IP range
        example_range = IPRange(
            name="Example Office Network",
            network_address="192.168.1.0",
            cidr=24,
            gateway="192.168.1.1",
            dns_servers=json.dumps(["8.8.8.8", "8.8.4.4"]),
            domain_name="office.local",
            pool_start="192.168.1.100",
            pool_end="192.168.1.200",
            description="Example office network for demonstration",
            is_active=True
        )
        db.add(example_range)
        db.flush()  # Get the ID

        # Create example device
        example_device = Device(
            hostname="example-printer",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.10",
            ip_range_id=example_range.id,
            description="Example HP LaserJet printer",
            is_active=True,
            created_by=admin.id
        )
        db.add(example_device)

        db.commit()

        print("✅ Example network 'Example Office Network' (192.168.1.0/24) created")
        print("✅ Example device 'example-printer' (192.168.1.10) created")
        print("🎉 Database initialized with example data!")

    except Exception as e:
        print(f"❌ Error creating example data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_example_data()
