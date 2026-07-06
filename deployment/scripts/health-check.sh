#!/bin/bash
# SkinGuard Production Health Check Script
# Verifies all production services are healthy

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKEND_URL="${BACKEND_URL:-https://api.skinguard.com}"
FRONTEND_URL="${FRONTEND_URL:-https://skinguard.com}"
DATABASE_URL="${DATABASE_URL}"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}SkinGuard Production Health Check${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

FAILED_CHECKS=0

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((FAILED_CHECKS++))
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check backend health
check_backend() {
    echo "Checking backend health..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)
    
    if [ "$response" -eq 200 ]; then
        print_status "Backend is healthy (HTTP $response)"
        
        # Get detailed health info
        health_data=$(curl -s "$BACKEND_URL/health" 2>/dev/null)
        echo "  Response: $health_data"
    else
        print_error "Backend health check failed (HTTP $response)"
    fi
}

# Check frontend
check_frontend() {
    echo "Checking frontend..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null)
    
    if [ "$response" -eq 200 ]; then
        print_status "Frontend is accessible (HTTP $response)"
    else
        print_error "Frontend check failed (HTTP $response)"
    fi
}

# Check database connection
check_database() {
    echo "Checking database connection..."
    
    if [ -z "$DATABASE_URL" ]; then
        print_warning "DATABASE_URL not set, skipping database check"
        return
    fi
    
    if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
        print_status "Database connection successful"
        
        # Check table count
        table_count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null | xargs)
        echo "  Tables: $table_count"
    else
        print_error "Database connection failed"
    fi
}

# Check API authentication
check_auth() {
    echo "Checking API authentication..."
    
    # Try to access a protected endpoint without auth (should fail with 401)
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/reports" 2>/dev/null)
    
    if [ "$response" -eq 401 ]; then
        print_status "Authentication is working (HTTP $response)"
    else
        print_warning "Unexpected auth response (HTTP $response)"
    fi
}

# Check API endpoints
check_api_endpoints() {
    echo "Checking critical API endpoints..."
    
    # Health endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)
    if [ "$response" -eq 200 ]; then
        print_status "Health endpoint: OK"
    else
        print_error "Health endpoint: FAILED (HTTP $response)"
    fi
    
    # Docs endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs" 2>/dev/null)
    if [ "$response" -eq 200 ]; then
        print_status "API docs endpoint: OK"
    else
        print_warning "API docs endpoint: FAILED (HTTP $response)"
    fi
}

# Check SSL certificate
check_ssl() {
    echo "Checking SSL certificates..."
    
    # Check backend SSL
    if echo | openssl s_client -connect api.skinguard.com:443 -servername api.skinguard.com 2>/dev/null | grep -q "Verify return code: 0"; then
        print_status "Backend SSL certificate is valid"
    else
        print_error "Backend SSL certificate check failed"
    fi
    
    # Check frontend SSL
    if echo | openssl s_client -connect skinguard.com:443 -servername skinguard.com 2>/dev/null | grep -q "Verify return code: 0"; then
        print_status "Frontend SSL certificate is valid"
    else
        print_error "Frontend SSL certificate check failed"
    fi
}

# Check DNS resolution
check_dns() {
    echo "Checking DNS resolution..."
    
    if nslookup api.skinguard.com > /dev/null 2>&1; then
        print_status "Backend DNS resolves correctly"
    else
        print_error "Backend DNS resolution failed"
    fi
    
    if nslookup skinguard.com > /dev/null 2>&1; then
        print_status "Frontend DNS resolves correctly"
    else
        print_error "Frontend DNS resolution failed"
    fi
}

# Check response times
check_performance() {
    echo "Checking response times..."
    
    # Backend response time
    backend_time=$(curl -s -o /dev/null -w "%{time_total}" "$BACKEND_URL/health" 2>/dev/null)
    backend_ms=$(echo "$backend_time * 1000" | bc)
    
    if (( $(echo "$backend_time < 1.0" | bc -l) )); then
        print_status "Backend response time: ${backend_ms}ms"
    else
        print_warning "Backend response time slow: ${backend_ms}ms"
    fi
    
    # Frontend response time
    frontend_time=$(curl -s -o /dev/null -w "%{time_total}" "$FRONTEND_URL" 2>/dev/null)
    frontend_ms=$(echo "$frontend_time * 1000" | bc)
    
    if (( $(echo "$frontend_time < 3.0" | bc -l) )); then
        print_status "Frontend response time: ${frontend_ms}ms"
    else
        print_warning "Frontend response time slow: ${frontend_ms}ms"
    fi
}

# Main health check
main() {
    echo ""
    
    check_backend
    echo ""
    
    check_frontend
    echo ""
    
    check_database
    echo ""
    
    check_auth
    echo ""
    
    check_api_endpoints
    echo ""
    
    check_ssl
    echo ""
    
    check_dns
    echo ""
    
    check_performance
    echo ""
    
    # Summary
    echo -e "${BLUE}=========================================${NC}"
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${GREEN}All health checks passed!${NC}"
        echo -e "${BLUE}=========================================${NC}"
        exit 0
    else
        echo -e "${RED}$FAILED_CHECKS health check(s) failed${NC}"
        echo -e "${BLUE}=========================================${NC}"
        exit 1
    fi
}

# Run health check
main
