"""
Check whatsapp_no values in doctors table
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    cursor.execute("""
        SELECT id, user_id, clinic_name, whatsapp_no
        FROM doctors
    """)
    
    doctors = cursor.fetchall()
    
    print("=== DOCTOR WHATSAPP NUMBERS ===")
    for doc_id, user_id, clinic_name, whatsapp_no in doctors:
        print(f"\nClinic: {clinic_name}")
        print(f"WhatsApp: {whatsapp_no} (type: {type(whatsapp_no)})")

except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
