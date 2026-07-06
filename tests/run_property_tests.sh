#!/bin/bash

# SkinGuard Property Test Runner
# Runs property-based tests for database referential integrity

set -e

echo "=========================================="
echo "SkinGuard Property Tests"
echo "=========================================="
echo ""

# Check if dependencies are installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip install -r tests/requirements.txt
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found"
    echo "Property tests require DATABASE_URL to be set"
    echo "Tests will be skipped without database connection"
    echo ""
fi

# Run property tests
echo "Running property-based tests..."
echo ""

python -m pytest tests/property/test_database_properties.py \
    -v \
    --tb=short \
    -m property \
    --hypothesis-show-statistics

echo ""
echo "=========================================="
echo "Property tests complete"
echo "=========================================="
