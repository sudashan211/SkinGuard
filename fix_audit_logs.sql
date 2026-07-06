-- Quick fix: Add missing metadata column to audit_logs table
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Verify the column was added
SELECT 'metadata column added successfully!' AS message;
