#!/bin/bash

# SkinGuard Database Setup Script
# This script automates the database setup process
# Requirements: 12.1, 12.4, 12.5

set -e  # Exit on error

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_info "Please create a .env file with the following variables:"
        echo ""
        echo "DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres"
        echo "SUPABASE_URL=https://your-project.supabase.co"
        echo "SUPABASE_ANON_KEY=your-anon-key"
        echo "SUPABASE_SERVICE_ROLE_KEY=your-service-role-key"
        echo ""
        exit 1
    fi
    print_success ".env file found"
}

# Check if required tools are installed
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check for psql
    if command -v psql &> /dev/null; then
        print_success "psql is installed"
    else
        print_warning "psql is not installed (optional for direct database access)"
    fi
    
    # Check for Python
    if command -v python3 &> /dev/null; then
        print_success "Python 3 is installed"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check for pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 is installed"
    else
        print_error "pip3 is required but not installed"
        exit 1
    fi
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    pip3 install -q psycopg2-binary python-dotenv
    print_success "Python dependencies installed"
}

# Run migrations
run_migrations() {
    print_header "Running Database Migrations"
    
    # Load environment variables
    source .env
    
    if [ -z "$DATABASE_URL" ]; then
        print_error "DATABASE_URL not set in .env file"
        exit 1
    fi
    
    # Extract connection details from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)/\1/p')
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\(.*\):.*/\1/p')
    
    print_info "Database host: $DB_HOST"
    print_info "Database port: $DB_PORT"
    print_info "Database name: $DB_NAME"
    
    # Check if psql is available
    if command -v psql &> /dev/null; then
        print_info "Running migrations with psql..."
        
        # Migration 001: Initial Schema
        print_info "Running migration 001_initial_schema.sql..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/migrations/001_initial_schema.sql
        print_success "Migration 001 completed"
        
        # Migration 002: RLS Policies
        print_info "Running migration 002_rls_policies.sql..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/migrations/002_rls_policies.sql
        print_success "Migration 002 completed"
        
        # Migration 003: Storage Setup
        print_info "Running migration 003_storage_setup.sql..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/migrations/003_storage_setup.sql
        print_success "Migration 003 completed"
        
        print_success "All migrations completed successfully"
    else
        print_warning "psql not available. Please run migrations manually:"
        print_info "1. Go to your Supabase Dashboard"
        print_info "2. Navigate to SQL Editor"
        print_info "3. Copy and paste each migration file in order:"
        print_info "   - database/migrations/001_initial_schema.sql"
        print_info "   - database/migrations/002_rls_policies.sql"
        print_info "   - database/migrations/003_storage_setup.sql"
    fi
}

# Create storage bucket
create_storage_bucket() {
    print_header "Storage Bucket Setup"
    
    print_warning "Storage bucket must be created manually via Supabase Dashboard"
    print_info "Please follow these steps:"
    echo ""
    echo "1. Go to your Supabase Dashboard"
    echo "2. Navigate to Storage section"
    echo "3. Click 'Create bucket'"
    echo "4. Configure as follows:"
    echo "   - Name: medical-images"
    echo "   - Public: false (private)"
    echo "   - File size limit: 10MB"
    echo "   - Allowed MIME types: image/jpeg, image/png, image/jpg"
    echo ""
    
    read -p "Press Enter once you've created the storage bucket..."
    print_success "Storage bucket setup acknowledged"
}

# Verify setup
verify_setup() {
    print_header "Verifying Database Setup"
    
    print_info "Running verification script..."
    python3 database/scripts/verify_setup.py
    
    if [ $? -eq 0 ]; then
        print_success "Database setup verified successfully!"
    else
        print_error "Database verification failed. Please review the output above."
        exit 1
    fi
}

# Main setup flow
main() {
    print_header "SkinGuard Database Setup"
    
    # Step 1: Check environment
    print_info "Step 1: Checking environment..."
    check_env_file
    check_dependencies
    
    # Step 2: Install dependencies
    print_info "\nStep 2: Installing dependencies..."
    install_python_deps
    
    # Step 3: Run migrations
    print_info "\nStep 3: Running migrations..."
    run_migrations
    
    # Step 4: Create storage bucket
    print_info "\nStep 4: Setting up storage..."
    create_storage_bucket
    
    # Step 5: Verify setup
    print_info "\nStep 5: Verifying setup..."
    verify_setup
    
    # Success message
    print_header "Setup Complete!"
    print_success "Database is ready for use"
    print_info "Next steps:"
    echo "  1. Configure your backend to use the database"
    echo "  2. Run the backend API server"
    echo "  3. Test the complete system"
    echo ""
}

# Run main function
main
