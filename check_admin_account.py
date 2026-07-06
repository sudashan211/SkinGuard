"""
Check if there's an admin account in the database
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    cursor.execute("""
        SELECT id, email, full_name, role, verified
        FROM profiles
        WHERE role = 'admin'
    """)
    
    admins = cursor.fetchall()
    
    if admins:
        print("=== ADMIN ACCOUNTS ===")
        for admin_id, email, full_name, role, verified in admins:
            print(f"Email: {email}")
            print(f"Name: {full_name}")
            print(f"Verified: {verified}")
            print("-" * 50)
    else:
        print("No admin accounts found in the database.")
        print("\nYou need to create an admin account.")

except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
