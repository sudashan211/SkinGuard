"""
Script to reset user password in PostgreSQL database
Run this with: python reset_password.py
"""
import bcrypt
import psycopg2

# Database connection
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

# User credentials
EMAIL = "sudashanrao0702@gmail.com"
NEW_PASSWORD = "Password123"

# Hash the password
password_bytes = NEW_PASSWORD.encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password_bytes, salt)
password_hash = hashed.decode('utf-8')

# Update database
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute(
    "UPDATE profiles SET password_hash = %s WHERE email = %s",
    (password_hash, EMAIL)
)

conn.commit()
rows_updated = cursor.rowcount

cursor.close()
conn.close()

print(f"Password updated for {EMAIL}")
print(f"Rows updated: {rows_updated}")
print(f"New password: {NEW_PASSWORD}")
