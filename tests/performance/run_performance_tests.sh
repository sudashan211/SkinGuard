#!/bin/bash

# Performance Testing Suite for SkinGuard
# Runs all performance tests and generates a comprehensive report

set -e

echo "=========================================="
echo "SkinGuard Performance Testing Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running${NC}"
    echo "Please start the backend server: cd backend && uvicorn app.main:app --reload"
    exit 1
fi

# Check if frontend is running
echo "Checking if frontend is running..."
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠ Frontend is not running${NC}"
    echo "Some tests may be skipped. Start frontend: cd frontend && npm run dev"
fi

echo ""
echo "=========================================="
echo "1. Backend Performance Tests"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# Run AI performance tests
echo "Running AI performance tests..."
python -m pytest performance/test_ai_performance.py -v -s -m performance

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ AI performance tests passed${NC}"
else
    echo -e "${RED}✗ AI performance tests failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "2. Load Testing (Optional)"
echo "=========================================="
echo ""

read -p "Run load test? This will take 5 minutes (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running load test with 50 users for 5 minutes..."
    cd performance
    locust -f locustfile.py --host=http://localhost:8000 \
           --users 50 --spawn-rate 5 --run-time 5m --headless
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Load test completed${NC}"
    else
        echo -e "${RED}✗ Load test failed${NC}"
    fi
    cd ..
else
    echo "Skipping load test"
fi

echo ""
echo "=========================================="
echo "3. Frontend Performance Tests"
echo "=========================================="
echo ""

if curl -s http://localhost:3000 > /dev/null; then
    cd ../frontend
    
    echo "Running E2E performance tests..."
    npm run test:performance
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend performance tests passed${NC}"
    else
        echo -e "${RED}✗ Frontend performance tests failed${NC}"
    fi
    
    cd ../tests
else
    echo -e "${YELLOW}⚠ Skipping frontend tests (frontend not running)${NC}"
fi

echo ""
echo "=========================================="
echo "4. Bundle Analysis"
echo "=========================================="
echo ""

cd ../frontend

echo "Building and analyzing bundle..."
npm run build

# Check bundle size
BUNDLE_SIZE=$(du -sh dist/assets/*.js | awk '{print $1}')
echo "Bundle size: $BUNDLE_SIZE"

cd ../tests

echo ""
echo "=========================================="
echo "Performance Testing Complete"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - AI Performance: Check test output above"
echo "  - Load Testing: Check Locust report"
echo "  - Frontend Performance: Check Playwright report"
echo "  - Bundle Size: $BUNDLE_SIZE"
echo ""
echo "Next steps:"
echo "  1. Review test results"
echo "  2. Check performance metrics"
echo "  3. Run Lighthouse audit: cd frontend && npm run lighthouse"
echo "  4. Monitor production metrics"
echo ""
