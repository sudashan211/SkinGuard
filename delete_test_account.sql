-- Delete the test account created during testing
-- Run this in Supabase SQL Editor

-- Delete from profiles table (this will cascade to related tables)
DELETE FROM profiles WHERE email = 'sudashanrao0702@gmail.com';

-- Verify deletion
SELECT 'Test account deleted successfully!' AS message;
