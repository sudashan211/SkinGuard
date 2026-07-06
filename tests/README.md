# SkinGuard Test Suite

This directory contains all tests for the SkinGuard AI Skin Cancer Screening Platform.

## Test Structure

```
tests/
├── property/                    # Property-based tests
│   └── test_database_properties.py
├── unit/                        # Unit tests (to be added)
├── integration/                 # Integration tests (to be added)
├── e2e/                        # End-to-end tests (to be added)
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Test dependencies
└── README.md                   # This file
```

## Test Types

### Property-Based Tests (`property/`)
Tests that verify universal properties hold across all inputs using randomized testing with Hypothesis.

**Current tests:**
- `test_database_properties.py` - Database referential integrity tests (Property 33)
- `test_database_properties.py` - User registration and authentication tests (Properties 1, 2, 4)
- `test_database_properties.py` - Patient profile validation tests (Properties 3, 5, 6, 7)

### Unit Tests (`unit/`)
Tests that verify specific examples, edge cases, and error conditions.

**To be added:**
- Authentication tests
- AI processing tests
- API endpoint tests
- Data validation tests

### Integration Tests (`integration/`)
Tests that verify multiple components work together correctly.

**To be added:**
- Complete upload flow tests
- Appointment booking flow tests
- Doctor verification flow tests

### End-to-End Tests (`e2e/`)
Tests that verify complete user journeys from start to finish.

**To be added:**
- Patient journey tests
- Doctor journey tests
- Admin workflow tests

## Setup

### Install Dependencies

```bash
# Install test dependencies
pip install -r tests/requirements.txt
```

### Configure Environment

Create a `.env` file in the project root with database credentials:

```env
DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Property-based tests only
pytest tests/property/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/
```

### Run Specific Test File

```bash
pytest tests/property/test_database_properties.py
```

### Run Specific Test Function

```bash
pytest tests/property/test_database_properties.py::test_patient_data_referential_integrity
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Property Tests with More Examples

```bash
# Run with 1000 examples instead of default 100
pytest tests/property/ --hypothesis-profile=thorough
```

## Property-Based Testing

Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/) to generate random test data and verify that properties hold across all inputs.

### Configuration

- **Default examples**: 100 per test
- **Deadline**: None (no timeout)
- **Profiles**: default, thorough (1000 examples)

### Writing Property Tests

```python
from hypothesis import given, strategies as st

@given(value=st.integers())
def test_property(value):
    """Test that property holds for all integers"""
    assert some_property(value)
```

### Test Tags

Each property test includes:
- Feature name: `derman-ai-skin-screening`
- Property number: From design document
- Property description: What is being tested
- Requirements: Which requirements it validates

Example:
```python
# Feature: derman-ai-skin-screening, Property 33: Referential Integrity Enforcement
@given(profile=valid_profile())
def test_referential_integrity(db_cursor, profile):
    """
    Property 33: Referential Integrity Enforcement
    Validates: Requirements 12.4, 12.5
    """
    # Test implementation
```

## Database Tests

Database tests require a running Supabase instance with the schema applied.

### Prerequisites

1. Supabase project created
2. Database migrations applied
3. `DATABASE_URL` environment variable set

### Test Isolation

Database tests use transactions with automatic rollback:
- Each test runs in a transaction
- Changes are rolled back after each test
- No test data persists in the database

### Fixtures

- `db_connection`: Module-scoped database connection
- `db_cursor`: Function-scoped cursor with automatic rollback

## Continuous Integration

Tests should run on every commit:

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r tests/requirements.txt
      - name: Run property tests
        run: pytest tests/property/ -v
      - name: Run unit tests
        run: pytest tests/unit/ -v
```

## Test Coverage Goals

- **Property tests**: All 93 correctness properties from design document
- **Unit tests**: 80%+ code coverage
- **Integration tests**: All critical user flows
- **E2E tests**: Patient and doctor journeys

## Current Status

### Completed
- ✅ Property test for referential integrity (Property 33)
- ✅ Property tests for user registration and authentication (Properties 1, 2, 4)
- ✅ Property tests for patient profile validation (Properties 3, 5, 6, 7)
- ✅ Test infrastructure setup
- ✅ Pytest configuration
- ✅ Database test fixtures

### In Progress
- 🔄 Additional property tests (Properties 1-92)
- 🔄 Unit tests for backend components
- 🔄 Integration tests for API flows

### Planned
- ⏳ E2E tests for user journeys
- ⏳ Performance tests
- ⏳ Security tests

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
python -c "import psycopg2; import os; psycopg2.connect(os.getenv('DATABASE_URL'))"
```

### Hypothesis Issues

```bash
# Clear Hypothesis cache
rm -rf .hypothesis/
```

### Test Failures

```bash
# Run with full traceback
pytest --tb=long

# Run with pdb debugger on failure
pytest --pdb
```

## References

- Design Document: `.kiro/specs/derman-ai-skin-screening/design.md`
- Requirements: `.kiro/specs/derman-ai-skin-screening/requirements.md`
- Pytest Docs: https://docs.pytest.org/
- Hypothesis Docs: https://hypothesis.readthedocs.io/

## Support

For test-related issues:
1. Check test output for error messages
2. Verify database connection and schema
3. Review test documentation
4. Check Hypothesis examples for failing inputs
