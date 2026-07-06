-- Create doctor profile record in doctors table
-- Run this in pgAdmin Query Tool

INSERT INTO doctors (
    id,
    user_id,
    license_no,
    clinic_name,
    lat,
    lng,
    whatsapp_no,
    specialization,
    bio,
    education,
    certifications,
    languages,
    clinic_hours,
    average_rating,
    review_count,
    created_at,
    updated_at
)
SELECT 
    gen_random_uuid(),
    id as user_id,
    'MD-12345' as license_no,
    'SkinGuard Dermatology Clinic' as clinic_name,
    1.3521 as lat,
    103.8198 as lng,
    '+65-1234-5678' as whatsapp_no,
    'Dermatology' as specialization,
    'Experienced dermatologist specializing in skin cancer detection and treatment' as bio,
    'MD from Harvard Medical School, Dermatology Residency at Mayo Clinic' as education,
    'Board Certified Dermatologist, Fellow of American Academy of Dermatology' as certifications,
    'English, Mandarin, Malay' as languages,
    'Mon-Fri: 9AM-5PM, Sat: 9AM-1PM' as clinic_hours,
    4.8 as average_rating,
    0 as review_count,
    NOW() as created_at,
    NOW() as updated_at
FROM profiles
WHERE email = 'doctor@skinguard.com'
AND NOT EXISTS (
    SELECT 1 FROM doctors WHERE user_id = profiles.id
);
