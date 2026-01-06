-- Migration: Add last_seen column to devices table
-- This migration adds the last_seen timestamp column for tracking
-- device activity from DHCP logs

-- Add last_seen column
ALTER TABLE devices ADD COLUMN last_seen TIMESTAMP;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen);
