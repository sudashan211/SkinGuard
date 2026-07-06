-- Create doctor profile for Dr. Pratap in doctors table
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
    'MD-67890' as license_no,
    'Pratap Dermatology Center' as clinic_name,
    1.3521 as lat,
    103.8198 as lng,
    '+65-9876-5432' as whatsapp_no,
    'Dermatology' as specialization,
    'Experienced dermatologist specializing in skin conditions and cosmetic dermatology' as bio,
    'MBBS, MD Dermatology' as education,
    'Board Certified Dermatologist' as certifications,
    'English, Hindi, Tamil' as languages,
    'Mon-Sat: 9AM-6PM' as clinic_hours,
    4.5 as average_rating,
    0 as review_count,
    NOW() as created_at,
    NOW() as updated_at
FROM profiles
WHERE email = 'pratap@gmail.com'
AND NOT EXISTS (
    SELECT 1 FROM doctors WHERE user_id = profiles.id
);
