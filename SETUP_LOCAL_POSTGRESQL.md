# Setup Local PostgreSQL Database

## You Already Have: pgAdmin 4 ✅

## Step 1: Find Your PostgreSQL Password

Your PostgreSQL password was set during installation. Common defaults:
- Username: `postgres`
- Password: `postgres` OR the password you set during installation

## Step 2: Create Database

1. **Open pgAdmin 4**
2. **Connect to PostgreSQL**:
   - Server: localhost (or PostgreSQL 15/16)
   - Username: postgres
   - Password: (your password)
3. **Create Database**:
   - Right-click "Databases" → "Create" → "Database"
   - Database name: `skinguard`
   - Owner: postgres
   - Click "Save"

## Step 3: Run Database Setup Script

1. **In pgAdmin**, right-click `skinguard` database
2. Click "Query Tool"
3. **Open file**: `database_setup.sql` from your project
4. **Copy all SQL** and paste into Query Tool
5. **Click Execute** (or press F5)
6. You should see: "Database setup complete! All tables created successfully."

## Step 4: Update Database URL in .env

The `.env` file has been updated with:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/skinguard
```

**If your PostgreSQL password is different**, update it:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/skinguard
```

Replace `YOUR_PASSWORD` with your actual PostgreSQL password.

## Step 5: Install Required Python Package

The backend needs `psycopg2` to connect to PostgreSQL:

```bash
cd backend
pip install psycopg2-binary
```

## Step 6: Update Backend Code

I need to update the backend to use PostgreSQL instead of Supabase client.

## Step 7: Restart Backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Step 8: Test Account Creation

1. Go to http://localhost:3000
2. Create account with:
   - Email: sudashanrao0702@gmail.com
   - Password: Password123
   - Role: Patient
3. Should work with NO rate limits! ✅

## Benefits of Local PostgreSQL

✅ **No rate limits** - Create unlimited accounts
✅ **Faster** - Database is on your computer
✅ **Free forever** - No cloud costs
✅ **Full control** - You own the data
✅ **Production-ready** - Real PostgreSQL database

## Troubleshooting

### Can't connect to PostgreSQL?
- Make sure PostgreSQL service is running
- Check Windows Services → PostgreSQL should be "Running"
- Or restart: `net start postgresql-x64-15` (or your version)

### Wrong password?
- Update DATABASE_URL in `.env` with correct password
- Format: `postgresql://postgres:YOUR_PASSWORD@localhost:5432/skinguard`

### Tables not created?
- Make sure you selected `skinguard` database in pgAdmin
- Run the SQL script again
- Check for error messages in Query Tool

## Next Steps

Once database is set up, I'll update the backend code to use PostgreSQL directly instead of Supabase client.
