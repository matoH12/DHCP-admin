"""
Auto-generate DHCP configuration on startup
"""
from app.database import SessionLocal
from app.services.dhcp_generator import generate_and_save_config
from app.config import settings
import os


def init_dhcp_config():
    """Generate DHCP configuration file on startup"""
    db = SessionLocal()

    try:
        config_path = settings.DHCP_CONFIG_PATH

        # Always regenerate config to ensure it matches current database state
        print(f"🔧 Generating DHCP configuration...")

        content, file_path = generate_and_save_config(
            db,
            user_id=None,  # System-generated on startup
            save_to_db=False  # Don't save to DB history on auto-generation
        )

        print(f"✅ DHCP configuration generated: {file_path}")
        print(f"📊 Configuration size: {len(content)} bytes")

        # Show a preview of the Docker network subnet line
        for line in content.split('\n'):
            if 'Docker bridge network' in line or (line.strip().startswith('subnet') and 'Docker' in content[max(0, content.index(line)-200):content.index(line)]):
                print(f"   {line}")
                if line.strip().startswith('subnet'):
                    break

    except Exception as e:
        print(f"❌ Error generating DHCP config: {str(e)}")
        print(f"⚠️  DHCP server may fail to start without valid configuration")
    finally:
        db.close()


if __name__ == "__main__":
    init_dhcp_config()
