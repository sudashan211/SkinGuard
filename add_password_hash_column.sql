-- Add password_hash column to profiles table for PostgreSQL authentication
-- Run this in pgAdmin Query Tool

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Add comment
COMMENT ON COLUMN profiles.password_hash IS 'Hashed password for local PostgreSQL authentication';
