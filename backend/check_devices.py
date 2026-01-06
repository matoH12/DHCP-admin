#!/usr/bin/env python3
"""Check devices and their last_seen values"""
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.models.device import Device
from datetime import datetime

db = SessionLocal()
devices = db.query(Device).all()

print('=' * 80)
print('DEVICES IN DATABASE:')
print('=' * 80)

for device in devices:
    print(f'\nHostname:  {device.hostname}')
    print(f'MAC:       {device.mac_address}')
    print(f'IP:        {device.ip_address}')
    print(f'last_seen: {device.last_seen}')

    if device.last_seen:
        diff = datetime.utcnow() - device.last_seen
        minutes = diff.total_seconds() / 60
        hours = minutes / 60

        if minutes < 60:
            print(f'           ✅ Aktualizované pred {int(minutes)} minútami')
        elif hours < 24:
            print(f'           ⚠️  Aktualizované pred {int(hours)} hodinami')
        else:
            days = hours / 24
            print(f'           ❌ Aktualizované pred {int(days)} dňami')
    else:
        print(f'           ❌ Nikdy nebolo videné')

    print('-' * 80)

db.close()

print(f'\nTotal devices: {len(devices)}')
print('=' * 80)
