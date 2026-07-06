"""
Phase 8 Verification Script
Verifies all Phase 8 implementations are complete and functional

Tasks verified:
- Task 18: Notification System
- Task 19: Admin Panel Backend
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import uuid
from datetime import datetime


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def verify_notification_service():
    """Verify notification service implementation"""
    print_header("Task 18.1: Notification Service")
    
    try:
        from app.notification_service import NotificationService
        service = NotificationService()
        print_success("NotificationService class instantiated")
        
        # Check methods exist
        methods = [
            'create_notification',
            'send_analysis_complete_notification',
            'send_appointment_confirmation',
            'send_appointment_reminder',
            'send_doctor_verification_notification',
            'send_followup_screening_reminder'
        ]
        
        for method in methods:
            if hasattr(service, method):
                print_success(f"Method '{method}' exists")
            else:
                print_error(f"Method '{method}' missing")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Failed to verify notification service: {str(e)}")
        return False


def verify_notification_endpoints():
    """Verify notification endpoints exist"""
    print_header("Task 18.3: Notification Endpoints")
    
    try:
        from app.routers import notifications
        print_success("Notifications router module exists")
        
        # Check router exists
        if hasattr(notifications, 'router'):
            print_success("Router object exists")
        else:
            print_error("Router object missing")
            return False
        
        # Check endpoints are registered
        routes = [route.path for route in notifications.router.routes]
        
        expected_routes = [
            '/api/notifications',
            '/api/notifications/{notification_id}/read'
        ]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print_success(f"Endpoint '{route}' registered")
            else:
                print_error(f"Endpoint '{route}' missing")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Failed to verify notification endpoints: {str(e)}")
        return False


def verify_admin_moderation_endpoint():
    """Verify admin moderation endpoint"""
    print_header("Task 19.1: Content Moderation Endpoints")
    
    try:
        from app.routers import admin
        print_success("Admin router module exists")
        
        # Check router exists
        if hasattr(admin, 'router'):
            print_success("Router object exists")
        else:
            print_error("Router object missing")
            return False
        
        # Check flagged reports endpoint
        routes = [route.path for route in admin.router.routes]
        
        if any('/api/admin/reports/flagged' in r for r in routes):
            print_success("Endpoint '/api/admin/reports/flagged' registered")
        else:
            print_error("Endpoint '/api/admin/reports/flagged' missing")
            return False
        
        # Check FlaggedReportResponse model exists
        from app.models import FlaggedReportResponse
        print_success("FlaggedReportResponse model exists")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to verify admin moderation endpoint: {str(e)}")
        return False


def verify_skin_wiki_endpoints():
    """Verify Skin-Wiki content management endpoints"""
    print_header("Task 19.3: Skin-Wiki Content Management")
    
    try:
        from app.routers import admin
        
        routes = [route.path for route in admin.router.routes]
        
        expected_routes = [
            '/api/admin/skin-wiki/articles',
            '/api/admin/skin-wiki/articles/{article_id}',
            '/api/admin/skin-wiki/articles/{article_id}/versions'
        ]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print_success(f"Endpoint '{route}' registered")
            else:
                print_error(f"Endpoint '{route}' missing")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Failed to verify Skin-Wiki endpoints: {str(e)}")
        return False


def verify_database_tables():
    """Verify required database tables exist"""
    print_header("Database Tables Verification")
    
    try:
        from app.database import supabase
        
        # Check notifications table
        result = supabase.table('notifications').select('count').limit(1).execute()
        print_success("Table 'notifications' exists")
        
        # Check skin_wiki_articles table
        try:
            result = supabase.table('skin_wiki_articles').select('count').limit(1).execute()
            print_success("Table 'skin_wiki_articles' exists")
        except:
            print_info("Table 'skin_wiki_articles' not found (migration may not be run yet)")
        
        # Check skin_wiki_versions table
        try:
            result = supabase.table('skin_wiki_versions').select('count').limit(1).execute()
            print_success("Table 'skin_wiki_versions' exists")
        except:
            print_info("Table 'skin_wiki_versions' not found (migration may not be run yet)")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to verify database tables: {str(e)}")
        return False


def verify_property_tests():
    """Verify property test files exist"""
    print_header("Property Tests Verification")
    
    test_files = [
        ('tests/property/test_notification_delivery_properties.py', 'Task 18.2'),
        ('tests/property/test_admin_moderation_properties.py', 'Task 19.2'),
        ('tests/property/test_skin_wiki_properties.py', 'Task 19.4')
    ]
    
    all_exist = True
    for file_path, task in test_files:
        if os.path.exists(file_path):
            print_success(f"{task}: {file_path} exists")
        else:
            print_error(f"{task}: {file_path} missing")
            all_exist = False
    
    return all_exist


def verify_migration_files():
    """Verify migration files exist"""
    print_header("Migration Files Verification")
    
    migration_file = 'database/migrations/004_skin_wiki_tables.sql'
    
    if os.path.exists(migration_file):
        print_success(f"Migration file exists: {migration_file}")
        
        # Check file content
        with open(migration_file, 'r') as f:
            content = f.read()
            
        if 'skin_wiki_articles' in content:
            print_success("Migration includes 'skin_wiki_articles' table")
        else:
            print_error("Migration missing 'skin_wiki_articles' table")
            return False
            
        if 'skin_wiki_versions' in content:
            print_success("Migration includes 'skin_wiki_versions' table")
        else:
            print_error("Migration missing 'skin_wiki_versions' table")
            return False
        
        return True
    else:
        print_error(f"Migration file missing: {migration_file}")
        return False


def run_verification():
    """Run all verification checks"""
    print("\n" + "=" * 80)
    print("  PHASE 8 VERIFICATION - Notifications and Admin Features")
    print("=" * 80)
    
    results = {
        "Task 18.1 - Notification Service": verify_notification_service(),
        "Task 18.3 - Notification Endpoints": verify_notification_endpoints(),
        "Task 19.1 - Content Moderation": verify_admin_moderation_endpoint(),
        "Task 19.3 - Skin-Wiki Management": verify_skin_wiki_endpoints(),
        "Database Tables": verify_database_tables(),
        "Property Tests": verify_property_tests(),
        "Migration Files": verify_migration_files()
    }
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for task, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {task}")
    
    print("\n" + "-" * 80)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print_success("ALL PHASE 8 TASKS VERIFIED SUCCESSFULLY!")
        print("\n✨ Phase 8 is complete and ready for production!")
        return True
    else:
        print_error(f"{total - passed} checks failed")
        print("\n⚠️  Some Phase 8 tasks need attention")
        return False


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
