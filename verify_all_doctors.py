"""
Set all doctor accounts to verified=true
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Update all doctors to verified=true
    cursor.execute("""
        UPDATE profiles
        SET verified = true
        WHERE role = 'doctor'
        RETURNING email, full_name
    """)
    
    updated_doctors = cursor.fetchall()
    conn.commit()
    
    print("=== VERIFIED DOCTORS ===")
    for email, full_name in updated_doctors:
        print(f"✓ {email} ({full_name})")
    
    print(f"\nSuccessfully verified {len(updated_doctors)} doctors!")
    print("\nNow log out and log back in to get a new token with verified status.")

except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
