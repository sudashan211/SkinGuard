-- Set all doctor accounts to verified=true
-- Run this in pgAdmin Query Tool if doctors are not verified

UPDATE profiles
SET verified = true
WHERE role = 'doctor';

-- Show results
SELECT email, full_name, verified, role
FROM profiles
WHERE role = 'doctor'
ORDER BY created_at;
