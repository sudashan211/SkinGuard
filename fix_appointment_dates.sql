-- Check appointments with invalid dates
SELECT id, patient_id, doctor_id, scheduled_at, status, created_at
FROM appointments
WHERE scheduled_at IS NULL OR scheduled_at::text = 'Invalid Date';

-- Update appointments with null scheduled_at to a future date (tomorrow at 10 AM)
UPDATE appointments
SET scheduled_at = (NOW() + INTERVAL '1 day')::timestamp + TIME '10:00:00',
    updated_at = NOW()
WHERE scheduled_at IS NULL;

-- Verify the fix
SELECT id, patient_id, doctor_id, scheduled_at, status
FROM appointments
ORDER BY scheduled_at;
