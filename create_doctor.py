"""
Script to create a doctor account in PostgreSQL database
Run this with: python create_doctor.py
"""
import bcrypt
import psycopg2
import uuid

# Database connection
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

# Doctor credentials
EMAIL = "doctor@skinguard.com"
PASSWORD = "Doctor123"
FULL_NAME = "Dr. John Smith"
ROLE = "doctor"

# Hash the password
password_bytes = PASSWORD.encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password_bytes, salt)
password_hash = hashed.decode('utf-8')

# Generate UUID
user_id = str(uuid.uuid4())

# Insert into database
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Check if email already exists
    cursor.execute("SELECT id FROM profiles WHERE email = %s", (EMAIL,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"User with email {EMAIL} already exists!")
    else:
        # Insert new doctor profile
        cursor.execute(
            """
            INSERT INTO profiles (id, email, full_name, role, verified, language_preference, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, EMAIL, FULL_NAME, ROLE, False, "en", password_hash)
        )
        
        conn.commit()
        print(f"Doctor account created successfully!")
        print(f"Email: {EMAIL}")
        print(f"Password: {PASSWORD}")
        print(f"Role: {ROLE}")
        print(f"User ID: {user_id}")

except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
