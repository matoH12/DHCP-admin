# Database Migrations

## Adding last_seen column

This migration adds the `last_seen` column to the `devices` table for tracking device activity from DHCP logs.

### Method 1: Using Python script (Recommended)

Run the migration script from your project directory:

```bash
docker compose exec backend python migrations/migrate.py
```

### Method 2: Using SQL directly

If you prefer to run the SQL manually:

```bash
docker compose exec backend sqlite3 /app/data/dhcp-admin.db < migrations/add_last_seen.sql
```

### Method 3: Manual SQL execution

Connect to the database and run:

```bash
docker compose exec backend sqlite3 /app/data/dhcp-admin.db
```

Then execute:

```sql
ALTER TABLE devices ADD COLUMN last_seen TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen);
.exit
```

### Verification

To verify the migration was successful:

```bash
docker compose exec backend python -c "
from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)
columns = inspector.get_columns('devices')
has_last_seen = any(col['name'] == 'last_seen' for col in columns)

if has_last_seen:
    print('✓ Migration successful! Column last_seen exists.')
else:
    print('✗ Migration failed! Column last_seen does not exist.')
"
```

### After migration

Restart the backend container to ensure all changes are applied:

```bash
docker compose restart backend
```

## Troubleshooting

If you get "column already exists" error, the migration has already been applied.

If you get permission errors, ensure the data directory is writable by the container.
