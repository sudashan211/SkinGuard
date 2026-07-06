"""
Phase 8 Code Verification Script (No Database Required)
Verifies all Phase 8 code implementations are complete

Tasks verified:
- Task 18: Notification System
- Task 19: Admin Panel Backend
"""
import sys
import os
import ast


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


def verify_file_exists(file_path, description):
    """Verify a file exists"""
    if os.path.exists(file_path):
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description}: {file_path} NOT FOUND")
        return False


def verify_function_in_file(file_path, function_names):
    """Verify functions exist in a Python file"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        # Get all function definitions (including async and methods)
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
        
        all_found = True
        for func_name in function_names:
            if func_name in functions:
                print_success(f"  Function '{func_name}' found")
            else:
                print_error(f"  Function '{func_name}' NOT FOUND")
                all_found = False
        
        return all_found
    except Exception as e:
        print_error(f"  Error parsing file: {str(e)}")
        return False


def verify_class_in_file(file_path, class_names):
    """Verify classes exist in a Python file"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        all_found = True
        for class_name in class_names:
            if class_name in classes:
                print_success(f"  Class '{class_name}' found")
            else:
                print_error(f"  Class '{class_name}' NOT FOUND")
                all_found = False
        
        return all_found
    except Exception as e:
        print_error(f"  Error parsing file: {str(e)}")
        return False


def verify_string_in_file(file_path, search_strings):
    """Verify strings exist in a file"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_found = True
        for search_str in search_strings:
            if search_str in content:
                print_success(f"  Found: '{search_str}'")
            else:
                print_error(f"  NOT FOUND: '{search_str}'")
                all_found = False
        
        return all_found
    except Exception as e:
        print_error(f"  Error reading file: {str(e)}")
        return False


def verify_task_18_1():
    """Verify Task 18.1 - Notification Service"""
    print_header("Task 18.1: Notification Service Implementation")
    
    file_path = 'backend/app/notification_service.py'
    if not verify_file_exists(file_path, "Notification service file"):
        return False
    
    # Verify NotificationService class exists
    if not verify_class_in_file(file_path, ['NotificationService']):
        return False
    
    # Verify key methods exist
    methods = [
        'create_notification',
        'send_analysis_complete_notification',
        'send_appointment_confirmation',
        'send_appointment_reminder',
        'send_doctor_verification_notification',
        'send_followup_screening_reminder'
    ]
    
    return verify_function_in_file(file_path, methods)


def verify_task_18_2():
    """Verify Task 18.2 - Property Tests"""
    print_header("Task 18.2: Notification Delivery Property Tests")
    
    file_path = 'tests/property/test_notification_delivery_properties.py'
    if not verify_file_exists(file_path, "Property test file"):
        return False
    
    # Verify test functions exist
    tests = [
        'test_notification_delivery_creates_record',
        'test_notification_delivery_multiple_notifications',
        'test_notification_read_status_toggle'
    ]
    
    return verify_function_in_file(file_path, tests)


def verify_task_18_3():
    """Verify Task 18.3 - Notification Endpoints"""
    print_header("Task 18.3: Notification Endpoints")
    
    file_path = 'backend/app/routers/notifications.py'
    if not verify_file_exists(file_path, "Notifications router file"):
        return False
    
    # Verify endpoints exist
    endpoints = [
        'get_user_notifications',
        'mark_notification_read'
    ]
    
    return verify_function_in_file(file_path, endpoints)


def verify_task_19_1():
    """Verify Task 19.1 - Content Moderation Endpoints"""
    print_header("Task 19.1: Content Moderation Endpoints")
    
    file_path = 'backend/app/routers/admin.py'
    if not verify_file_exists(file_path, "Admin router file"):
        return False
    
    # Verify flagged reports endpoint exists
    if not verify_function_in_file(file_path, ['get_flagged_reports']):
        return False
    
    # Verify FlaggedReportResponse model exists
    model_file = 'backend/app/models.py'
    return verify_class_in_file(model_file, ['FlaggedReportResponse'])


def verify_task_19_2():
    """Verify Task 19.2 - Admin Moderation Property Tests"""
    print_header("Task 19.2: Admin Moderation Property Tests")
    
    file_path = 'tests/property/test_admin_moderation_properties.py'
    if not verify_file_exists(file_path, "Property test file"):
        return False
    
    # Verify test functions exist
    tests = [
        'test_flagged_content_filtering',
        'test_flagged_content_metadata_completeness',
        'test_flagged_content_ordering'
    ]
    
    return verify_function_in_file(file_path, tests)


def verify_task_19_3():
    """Verify Task 19.3 - Skin-Wiki Content Management"""
    print_header("Task 19.3: Skin-Wiki Content Management")
    
    file_path = 'backend/app/routers/admin.py'
    
    # Verify Skin-Wiki endpoints exist
    endpoints = [
        'create_skin_wiki_article',
        'update_skin_wiki_article',
        'get_article_version_history'
    ]
    
    if not verify_function_in_file(file_path, endpoints):
        return False
    
    # Verify migration file exists
    migration_file = 'database/migrations/004_skin_wiki_tables.sql'
    if not verify_file_exists(migration_file, "Skin-Wiki migration file"):
        return False
    
    # Verify migration contains required tables
    return verify_string_in_file(migration_file, [
        'skin_wiki_articles',
        'skin_wiki_versions',
        'CREATE TABLE'
    ])


def verify_task_19_4():
    """Verify Task 19.4 - Skin-Wiki Property Tests"""
    print_header("Task 19.4: Skin-Wiki Property Tests")
    
    file_path = 'tests/property/test_skin_wiki_properties.py'
    if not verify_file_exists(file_path, "Property test file"):
        return False
    
    # Verify test functions exist
    tests = [
        'test_content_update_persistence',
        'test_content_version_tracking',
        'test_version_history_content_preservation'
    ]
    
    return verify_function_in_file(file_path, tests)


def run_verification():
    """Run all verification checks"""
    print("\n" + "=" * 80)
    print("  PHASE 8 CODE VERIFICATION - Notifications and Admin Features")
    print("  (Code Structure Only - No Database Connection Required)")
    print("=" * 80)
    
    results = {
        "Task 18.1 - Notification Service": verify_task_18_1(),
        "Task 18.2 - Notification Property Tests": verify_task_18_2(),
        "Task 18.3 - Notification Endpoints": verify_task_18_3(),
        "Task 19.1 - Content Moderation": verify_task_19_1(),
        "Task 19.2 - Admin Moderation Property Tests": verify_task_19_2(),
        "Task 19.3 - Skin-Wiki Management": verify_task_19_3(),
        "Task 19.4 - Skin-Wiki Property Tests": verify_task_19_4()
    }
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for task, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {task}")
    
    print("\n" + "-" * 80)
    print(f"Results: {passed}/{total} checks passed ({int(passed/total*100)}%)")
    
    if passed == total:
        print_success("ALL PHASE 8 CODE VERIFIED SUCCESSFULLY!")
        print("\n✨ Phase 8 implementation is complete!")
        print("📝 Next step: Run database migrations and test with live database")
        return True
    else:
        print_error(f"{total - passed} checks failed")
        print("\n⚠️  Some Phase 8 code needs attention")
        return False


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
