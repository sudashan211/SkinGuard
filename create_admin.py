"""
Create an admin account
"""
import psycopg2
import bcrypt
import uuid

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

# Admin credentials
ADMIN_EMAIL = "admin@skinguard.com"
ADMIN_PASSWORD = "Admin123"
ADMIN_NAME = "System Administrator"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Check if admin already exists
    cursor.execute("SELECT id FROM profiles WHERE email = %s", (ADMIN_EMAIL,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"Admin account already exists: {ADMIN_EMAIL}")
    else:
        # Hash password
        password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin profile
        admin_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO profiles (id, email, full_name, role, verified, password_hash, language_preference, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (admin_id, ADMIN_EMAIL, ADMIN_NAME, 'admin', True, password_hash, 'en'))
        
        conn.commit()
        
        print("=== ADMIN ACCOUNT CREATED ===")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print(f"Name: {ADMIN_NAME}")
        print(f"Role: admin")
        print(f"Verified: True")
        print("\nYou can now log in with these credentials!")

except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cursor.close()
    conn.close()
