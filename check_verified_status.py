"""
Check the verified status of doctor accounts
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Get all doctor profiles with verified status
    print("=== DOCTOR VERIFIED STATUS ===")
    cursor.execute("""
        SELECT p.email, p.full_name, p.verified, p.role
        FROM profiles p
        WHERE p.role = 'doctor'
        ORDER BY p.created_at
    """)
    
    doctors = cursor.fetchall()
    
    for email, full_name, verified, role in doctors:
        status = "✓ VERIFIED" if verified else "✗ NOT VERIFIED"
        print(f"{email} ({full_name}): {status}")
    
    print(f"\nTotal: {len(doctors)} doctors")
    
    # Count verified vs not verified
    verified_count = sum(1 for d in doctors if d[2])
    print(f"Verified: {verified_count}")
    print(f"Not Verified: {len(doctors) - verified_count}")

except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
