"""
Script to create missing doctor profiles
Run this with: python fix_doctor_profiles.py
"""
import psycopg2
import uuid

# Database connection
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Find all doctors without profiles
    cursor.execute("""
        SELECT p.id, p.email, p.full_name
        FROM profiles p
        WHERE p.role = 'doctor'
        AND NOT EXISTS (
            SELECT 1 FROM doctors d WHERE d.user_id = p.id
        )
    """)
    
    missing_doctors = cursor.fetchall()
    
    if not missing_doctors:
        print("All doctors already have profiles!")
    else:
        print(f"Found {len(missing_doctors)} doctors without profiles")
        
        for user_id, email, full_name in missing_doctors:
            doctor_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'license_no': f'MD-{str(user_id)[:8]}',
                'clinic_name': f"{full_name}'s Clinic",
                'lat': 1.3521,
                'lng': 103.8198,
                'specialization': 'Dermatology',
                'bio': f'Dermatologist - {full_name}',
                'languages': 'English',
                'clinic_hours': 'Mon-Fri: 9AM-5PM',
                'average_rating': 0.0,
                'review_count': 0
            }
            
            cursor.execute("""
                INSERT INTO doctors (
                    id, user_id, license_no, clinic_name, lat, lng,
                    specialization, bio, languages, clinic_hours,
                    average_rating, review_count, created_at, updated_at
                )
                VALUES (
                    %(id)s, %(user_id)s, %(license_no)s, %(clinic_name)s, %(lat)s, %(lng)s,
                    %(specialization)s, %(bio)s, %(languages)s, %(clinic_hours)s,
                    %(average_rating)s, %(review_count)s, NOW(), NOW()
                )
            """, doctor_data)
            
            print(f"✓ Created profile for: {email}")
        
        conn.commit()
        print(f"\nSuccessfully created {len(missing_doctors)} doctor profiles!")
        print("Now log out and log back in to see the changes.")

except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
