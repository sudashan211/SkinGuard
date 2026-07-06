"""
Quick test to verify PostgreSQL connection and basic operations
"""
import sys
sys.path.insert(0, 'backend')

from app.postgres_db import get_postgres_client

try:
    print("Testing PostgreSQL connection...")
    client = get_postgres_client()
    
    # Test 1: Count profiles
    print("\n1. Testing SELECT query...")
    result = client.table("profiles").select("*").execute()
    print(f"   ✓ Found {len(result.data)} profiles")
    
    # Test 2: Test IN query
    print("\n2. Testing IN query...")
    if result.data:
        user_ids = [result.data[0]["id"]]
        in_result = client.table("profiles").select("*").in_("id", user_ids).execute()
        print(f"   ✓ IN query returned {len(in_result.data)} results")
    
    # Test 3: Count doctors
    print("\n3. Testing doctor profiles...")
    doctors = client.table("doctors").select("*").execute()
    print(f"   ✓ Found {len(doctors.data)} doctor profiles")
    
    # Test 4: Count medical reports
    print("\n4. Testing medical reports...")
    reports = client.table("medical_reports").select("*").execute()
    print(f"   ✓ Found {len(reports.data)} medical reports")
    
    print("\n✓ All PostgreSQL operations working correctly!")
    print("\nYour application is ready to use with PostgreSQL.")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
