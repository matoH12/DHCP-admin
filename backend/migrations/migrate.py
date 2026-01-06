#!/usr/bin/env python3
"""
Database migration script to add last_seen column to devices table

Usage:
    docker compose exec backend python migrations/migrate.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.database import engine

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)

def add_last_seen_column():
    """Add last_seen column to devices table if it doesn't exist"""
    print("Checking database schema...")

    if check_column_exists('devices', 'last_seen'):
        print("✓ Column 'last_seen' already exists in devices table")
        return True

    print("Adding 'last_seen' column to devices table...")

    try:
        with engine.connect() as conn:
            # Add the column
            conn.execute(text('ALTER TABLE devices ADD COLUMN last_seen TIMESTAMP'))
            conn.commit()
            print("✓ Column 'last_seen' added successfully")

            # Create index
            try:
                conn.execute(text('CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen)'))
                conn.commit()
                print("✓ Index created successfully")
            except Exception as e:
                print(f"⚠️  Index creation skipped: {e}")

            return True
    except Exception as e:
        print(f"✗ Error adding column: {e}")
        return False

def main():
    """Run migration"""
    print("=" * 60)
    print("DHCP Admin - Database Migration")
    print("Adding last_seen column to devices table")
    print("=" * 60)
    print()

    success = add_last_seen_column()

    print()
    print("=" * 60)
    if success:
        print("✓ Migration completed successfully!")
    else:
        print("✗ Migration failed!")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
