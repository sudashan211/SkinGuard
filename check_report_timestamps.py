"""
Check the format of created_at timestamps in medical_reports
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    cursor.execute("""
        SELECT id, patient_id, status, created_at, updated_at
        FROM medical_reports
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    reports = cursor.fetchall()
    
    print("=== MEDICAL REPORTS TIMESTAMPS ===")
    for report_id, patient_id, status, created_at, updated_at in reports:
        print(f"\nReport ID: {report_id}")
        print(f"Status: {status}")
        print(f"Created At: {created_at} (type: {type(created_at)})")
        print(f"Updated At: {updated_at} (type: {type(updated_at)})")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cursor.close()
    conn.close()
