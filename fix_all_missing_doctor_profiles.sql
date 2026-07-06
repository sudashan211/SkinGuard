-- Create doctor profiles for all doctor accounts that are missing them
-- Run this in pgAdmin Query Tool

INSERT INTO doctors (
    id,
    user_id,
    license_no,
    clinic_name,
    lat,
    lng,
    specialization,
    bio,
    languages,
    clinic_hours,
    average_rating,
    review_count,
    created_at,
    updated_at
)
SELECT 
    gen_random_uuid() as id,
    p.id as user_id,
    'MD-' || substring(p.id::text, 1, 8) as license_no,
    p.full_name || '''s Clinic' as clinic_name,
    1.3521 as lat,
    103.8198 as lng,
    'Dermatology' as specialization,
    'Dermatologist - ' || p.full_name as bio,
    'English' as languages,
    'Mon-Fri: 9AM-5PM' as clinic_hours,
    0.0 as average_rating,
    0 as review_count,
    NOW() as created_at,
    NOW() as updated_at
FROM profiles p
WHERE p.role = 'doctor'
AND NOT EXISTS (
    SELECT 1 FROM doctors d WHERE d.user_id = p.id
);

-- Show results
SELECT COUNT(*) as "Doctors Created" FROM doctors;
