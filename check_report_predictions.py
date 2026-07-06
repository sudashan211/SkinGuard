"""
Check ai_prediction data in medical_reports
"""
import psycopg2
import json

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/skinguard"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    cursor.execute("""
        SELECT id, status, ai_prediction
        FROM medical_reports
        ORDER BY created_at DESC
    """)
    
    reports = cursor.fetchall()
    
    print("=== MEDICAL REPORTS AI PREDICTIONS ===")
    for report_id, status, ai_prediction in reports:
        print(f"\nReport ID: {report_id}")
        print(f"Status: {status}")
        print(f"AI Prediction type: {type(ai_prediction)}")
        print(f"AI Prediction: {ai_prediction}")
        
        if ai_prediction:
            print(f"  Keys: {ai_prediction.keys() if isinstance(ai_prediction, dict) else 'N/A'}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cursor.close()
    conn.close()
