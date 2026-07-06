-- Migration: Add deletion_scheduled_at field to profiles table
-- Requirements: 18.3
-- Description: Adds field to track scheduled account deletions with 30-day grace period

-- Add deletion_scheduled_at column to profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS deletion_scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT NULL;

-- Add index for efficient querying of scheduled deletions
CREATE INDEX IF NOT EXISTS idx_profiles_deletion_scheduled 
ON profiles(deletion_scheduled_at) 
WHERE deletion_scheduled_at IS NOT NULL;

-- Add comment
COMMENT ON COLUMN profiles.deletion_scheduled_at IS 'Timestamp when account deletion is scheduled to occur (30 days after deletion request)';
