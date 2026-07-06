#!/usr/bin/env python3
"""
SkinGuard Database Setup Verification Script

This script verifies that the database schema is correctly set up with all
required tables, indexes, triggers, and RLS policies.

Requirements: 12.1, 12.4, 12.5
"""

import os
import sys
from typing import List, Dict, Tuple
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(message: str):
    print(f"{GREEN}✓{RESET} {message}")

def print_error(message: str):
    print(f"{RED}✗{RESET} {message}")

def print_warning(message: str):
    print(f"{YELLOW}⚠{RESET} {message}")

def print_info(message: str):
    print(f"{BLUE}ℹ{RESET} {message}")

def get_db_connection():
    """Create database connection from environment variables"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'postgres'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
        return conn
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        sys.exit(1)

def check_extensions(cursor) -> bool:
    """Verify required PostgreSQL extensions are installed"""
    print_info("Checking PostgreSQL extensions...")
    
    required_extensions = ['uuid-ossp', 'postgis']
    cursor.execute("""
        SELECT extname FROM pg_extension
        WHERE extname IN ('uuid-ossp', 'postgis')
    """)
    
    installed = [row[0] for row in cursor.fetchall()]
    
    all_installed = True
    for ext in required_extensions:
        if ext in installed:
            print_success(f"Extension '{ext}' is installed")
        else:
            print_error(f"Extension '{ext}' is NOT installed")
            all_installed = False
    
    return all_installed

def check_tables(cursor) -> bool:
    """Verify all required tables exist"""
    print_info("\nChecking database tables...")
    
    required_tables = [
        'profiles',
        'patient_data',
        'doctors',
        'medical_reports',
        'appointments',
        'reviews',
        'notifications',
        'audit_logs'
    ]
    
    cursor.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename IN %s
    """, (tuple(required_tables),))
    
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    all_exist = True
    for table in required_tables:
        if table in existing_tables:
            print_success(f"Table '{table}' exists")
        else:
            print_error(f"Table '{table}' does NOT exist")
            all_exist = False
    
    return all_exist

def check_indexes(cursor) -> bool:
    """Verify performance indexes are created"""
    print_info("\nChecking database indexes...")
    
    required_indexes = [
        ('profiles', 'idx_profiles_role'),
        ('profiles', 'idx_profiles_verified'),
        ('profiles', 'idx_profiles_email'),
        ('patient_data', 'idx_patient_data_user'),
        ('doctors', 'idx_doctors_location'),
        ('doctors', 'idx_doctors_user_id'),
        ('medical_reports', 'idx_reports_patient'),
        ('medical_reports', 'idx_reports_status'),
        ('medical_reports', 'idx_reports_risk'),
        ('medical_reports', 'idx_reports_created'),
        ('appointments', 'idx_appointments_patient'),
        ('appointments', 'idx_appointments_doctor'),
        ('appointments', 'idx_appointments_scheduled'),
        ('reviews', 'idx_reviews_doctor'),
        ('reviews', 'idx_reviews_rating'),
        ('notifications', 'idx_notifications_user'),
        ('notifications', 'idx_notifications_read'),
        ('notifications', 'idx_notifications_created'),
        ('audit_logs', 'idx_audit_logs_user'),
        ('audit_logs', 'idx_audit_logs_created'),
    ]
    
    cursor.execute("""
        SELECT tablename, indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
    """)
    
    existing_indexes = [(row[0], row[1]) for row in cursor.fetchall()]
    
    all_exist = True
    for table, index in required_indexes:
        if (table, index) in existing_indexes:
            print_success(f"Index '{index}' on '{table}' exists")
        else:
            print_warning(f"Index '{index}' on '{table}' does NOT exist")
            all_exist = False
    
    return all_exist

def check_rls(cursor) -> bool:
    """Verify Row Level Security is enabled on all tables"""
    print_info("\nChecking Row Level Security (RLS)...")
    
    required_tables = [
        'profiles',
        'patient_data',
        'doctors',
        'medical_reports',
        'appointments',
        'reviews',
        'notifications',
        'audit_logs'
    ]
    
    cursor.execute("""
        SELECT tablename, rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename IN %s
    """, (tuple(required_tables),))
    
    rls_status = {row[0]: row[1] for row in cursor.fetchall()}
    
    all_enabled = True
    for table in required_tables:
        if table in rls_status and rls_status[table]:
            print_success(f"RLS enabled on '{table}'")
        else:
            print_error(f"RLS NOT enabled on '{table}'")
            all_enabled = False
    
    return all_enabled

def check_policies(cursor) -> bool:
    """Verify RLS policies are created"""
    print_info("\nChecking RLS policies...")
    
    cursor.execute("""
        SELECT schemaname, tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
    """)
    
    policies = cursor.fetchall()
    policy_count = len(policies)
    
    if policy_count > 0:
        print_success(f"Found {policy_count} RLS policies")
        
        # Check for key policies
        policy_names = [p[2] for p in policies]
        
        key_policies = [
            'Users can view own profile',
            'Patients can view own reports',
            'Verified doctors can view reports',
            'Admins can view all reports'
        ]
        
        for policy in key_policies:
            if policy in policy_names:
                print_success(f"Policy '{policy}' exists")
            else:
                print_warning(f"Policy '{policy}' not found")
        
        return True
    else:
        print_error("No RLS policies found")
        return False

def check_triggers(cursor) -> bool:
    """Verify database triggers are created"""
    print_info("\nChecking database triggers...")
    
    cursor.execute("""
        SELECT tgname, tgrelid::regclass
        FROM pg_trigger
        WHERE tgname LIKE '%updated_at%' OR tgname LIKE '%rating%'
    """)
    
    triggers = cursor.fetchall()
    trigger_count = len(triggers)
    
    if trigger_count > 0:
        print_success(f"Found {trigger_count} triggers")
        for trigger_name, table_name in triggers:
            print_success(f"  - {trigger_name} on {table_name}")
        return True
    else:
        print_warning("No triggers found")
        return False

def check_constraints(cursor) -> bool:
    """Verify foreign key constraints for referential integrity"""
    print_info("\nChecking foreign key constraints...")
    
    cursor.execute("""
        SELECT
            tc.table_name,
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
    """)
    
    constraints = cursor.fetchall()
    constraint_count = len(constraints)
    
    if constraint_count > 0:
        print_success(f"Found {constraint_count} foreign key constraints")
        
        # Verify key constraints
        expected_constraints = [
            ('patient_data', 'profiles'),
            ('doctors', 'profiles'),
            ('medical_reports', 'profiles'),
            ('appointments', 'profiles'),
            ('appointments', 'doctors'),
        ]
        
        constraint_pairs = [(c[0], c[3]) for c in constraints]
        
        for table, ref_table in expected_constraints:
            if (table, ref_table) in constraint_pairs:
                print_success(f"  - {table} → {ref_table}")
            else:
                print_error(f"  - Missing: {table} → {ref_table}")
        
        return True
    else:
        print_error("No foreign key constraints found")
        return False

def check_storage_bucket():
    """Check if storage bucket exists (requires Supabase client)"""
    print_info("\nChecking storage bucket...")
    print_warning("Storage bucket verification requires Supabase client")
    print_info("Please verify manually in Supabase Dashboard:")
    print_info("  - Bucket name: 'medical-images'")
    print_info("  - Public: false")
    print_info("  - File size limit: 10MB")
    print_info("  - Allowed types: image/jpeg, image/png, image/jpg")
    return True

def main():
    """Main verification function"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}SkinGuard Database Setup Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Connect to database
    print_info("Connecting to database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    print_success("Connected to database\n")
    
    # Run all checks
    checks = [
        ("Extensions", check_extensions),
        ("Tables", check_tables),
        ("Indexes", check_indexes),
        ("RLS Enabled", check_rls),
        ("RLS Policies", check_policies),
        ("Triggers", check_triggers),
        ("Foreign Keys", check_constraints),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func(cursor)
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Error during {check_name} check: {e}")
            results.append((check_name, False))
    
    # Storage bucket check (doesn't use cursor)
    check_storage_bucket()
    
    # Close connection
    cursor.close()
    conn.close()
    
    # Print summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Verification Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{check_name:.<40} {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} checks passed{RESET}\n")
    
    if passed == total:
        print_success("✓ Database setup is complete and verified!")
        return 0
    else:
        print_error("✗ Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
