"""
Check the status of doctor accounts and profiles
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Get all profiles with role='doctor'
    print("=== ALL DOCTOR ACCOUNTS ===")
    cursor.execute("""
        SELECT p.id, p.email, p.full_name, p.role
        FROM profiles p
        WHERE p.role = 'doctor'
        ORDER BY p.created_at
    """)
    
    profiles = cursor.fetchall()
    print(f"Total doctor accounts: {len(profiles)}\n")
    
    for user_id, email, full_name, role in profiles:
        print(f"Email: {email}")
        print(f"Name: {full_name}")
        print(f"User ID: {user_id}")
        
        # Check if doctor profile exists
        cursor.execute("SELECT id FROM doctors WHERE user_id = %s", (user_id,))
        doctor_profile = cursor.fetchone()
        
        if doctor_profile:
            print(f"✓ Has doctor profile (ID: {doctor_profile[0]})")
        else:
            print("✗ MISSING doctor profile")
        print("-" * 50)

except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
