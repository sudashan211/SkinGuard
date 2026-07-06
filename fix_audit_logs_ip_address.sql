-- Add ip_address column to audit_logs table
-- Run this in pgAdmin Query Tool

ALTER TABLE audit_logs 
ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45);

-- Add comment
COMMENT ON COLUMN audit_logs.ip_address IS 'IP address of the user who performed the action';
