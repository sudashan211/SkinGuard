# Setting Up Database for Property-Based Tests

Property-based tests require a real database connection to test database constraints, referential integrity, and data persistence. This guide will help you set up the database connection.

## Quick Setup

### Option 1: Using Supabase (Recommended)

1. **Get your Supabase credentials:**
   - Go to your Supabase project dashboard
   - Navigate to Settings > Database
   - Copy the connection string under "Connection string" > "URI"
   - It should look like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

2. **Create .env file in tests directory:**
   ```bash
   cd tests
   cp .env.example .env
   ```

3. **Edit .env and add your DATABASE_URL:**
   ```env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

4. **Verify the connection:**
   ```bash
   python -c "import psycopg2; import os; from dotenv import load_dotenv; load_dotenv(); psycopg2.connect(os.getenv('DATABASE_URL')); print('✓ Database connection successful!')"
   ```

5. **Run the tests:**
   ```bash
   pytest property/test_database_properties.py -v
   ```

### Option 2: Using Local PostgreSQL

1. **Install PostgreSQL:**
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Mac: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql`

2. **Create a test database:**
   ```bash
   createdb skinguard_test
   ```

3. **Run migrations:**
   ```bash
   cd database
   psql -d skinguard_test -f migrations/001_initial_schema.sql
   psql -d skinguard_test -f migrations/002_rls_policies.sql
   ```

4. **Create .env file:**
   ```bash
   cd tests
   cp .env.example .env
   ```

5. **Edit .env and add your DATABASE_URL:**
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/skinguard_test
   ```
   (Replace `password` with your PostgreSQL password)

6. **Run the tests:**
   ```bash
   pytest property/test_database_properties.py -v
   ```

## What Gets Tested

The property-based tests verify:

### Patient Profile Tests (Task 4)
- **Property 5: Age Validation Bounds** - Ages must be 1-120
- **Property 6: Fitzpatrick Scale Validation** - Skin types must be I-VI
- **Property 7: Text Storage Without Truncation** - Family history stored completely
- **Property 3: Profile Update Persistence** - Updates are persisted correctly

### Authentication Tests
- **Property 1: User Registration Completeness** - All required fields present
- **Property 2: Authentication Round Trip** - Login tokens work correctly
- **Property 4: Role-Based Access Control** - Permissions enforced properly

### Database Integrity Tests
- **Property 33: Referential Integrity** - Foreign keys enforced
- Cascade deletes work correctly
- Invalid references are rejected

## Test Isolation

Don't worry about test data polluting your database:

- Each test runs in a **transaction**
- All changes are **automatically rolled back** after each test
- No test data persists in the database
- Tests can run in parallel safely

## Troubleshooting

### "DATABASE_URL not set - skipping database tests"

**Solution:** Create a `.env` file in the `tests/` directory with your DATABASE_URL.

### "could not connect to server"

**Possible causes:**
1. Database is not running
2. Wrong connection string
3. Firewall blocking connection
4. Wrong password

**Solutions:**
- Verify database is running: `pg_isready` (for local PostgreSQL)
- Check connection string format
- For Supabase: Verify project is not paused
- Test connection manually: `psql "postgresql://..."`

### "relation does not exist"

**Solution:** Run database migrations:
```bash
cd database
psql -d skinguard_test -f migrations/001_initial_schema.sql
```

### "permission denied for table"

**Solution:** Ensure you're using the service role key (not anon key) for Supabase, or have proper permissions for local PostgreSQL.

## Running Specific Tests

```bash
# Run all patient profile tests
pytest property/test_database_properties.py::test_age_validation_bounds \
       property/test_database_properties.py::test_fitzpatrick_scale_validation \
       property/test_database_properties.py::test_text_storage_without_truncation \
       property/test_database_properties.py::test_profile_update_persistence -v

# Run with more examples (thorough testing)
pytest property/test_database_properties.py -v --hypothesis-profile=thorough

# Run with verbose output and show print statements
pytest property/test_database_properties.py -v -s
```

## CI/CD Setup

For GitHub Actions or other CI/CD:

```yaml
- name: Run property tests
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
  run: |
    cd tests
    pytest property/ -v --hypothesis-profile=ci
```

Make sure to add `TEST_DATABASE_URL` as a secret in your repository settings.

## Next Steps

Once the database is configured:

1. Run all property tests: `pytest property/ -v`
2. Verify all tests pass
3. Continue with next tasks in the implementation plan

## Need Help?

- Check the main [tests/README.md](README.md) for more information
- Review the [design document](../.kiro/specs/derman-ai-skin-screening/design.md)
- Check [Hypothesis documentation](https://hypothesis.readthedocs.io/)
