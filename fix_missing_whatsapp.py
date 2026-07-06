"""
Set default whatsapp_no for doctors that have NULL
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Update doctors with NULL whatsapp_no
    cursor.execute("""
        UPDATE doctors
        SET whatsapp_no = '+65-0000-0000'
        WHERE whatsapp_no IS NULL
        RETURNING clinic_name
    """)
    
    updated = cursor.fetchall()
    conn.commit()
    
    print("=== UPDATED DOCTORS ===")
    for (clinic_name,) in updated:
        print(f"✓ {clinic_name}")
    
    print(f"\nUpdated {len(updated)} doctor profiles with default WhatsApp number")

except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
