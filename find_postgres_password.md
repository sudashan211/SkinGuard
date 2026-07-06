# Find Your PostgreSQL Password

Since pgAdmin 4 connects successfully but the password is encrypted, here's how to find it:

## Option 1: Check pgAdmin Connection (Easiest)

1. Open **pgAdmin 4**
2. In the left sidebar, **right-click** on your PostgreSQL server (e.g., "PostgreSQL 15")
3. Click **"Disconnect Server"**
4. **Right-click again** and select **"Connect Server"**
5. It will **ask for the password** - that's your password!
6. **Write it down** or remember it

## Option 2: Use a Test Password

Try entering this password in pgAdmin when it asks:
- Try: `admin`
- Try: `root`  
- Try: `1234`
- Try: Whatever you remember from installation

## Option 3: Reset Password (If you forgot)

If you can't remember, we can reset it:

1. Open **Command Prompt as Administrator**
2. Run:
```cmd
psql -U postgres
ALTER USER postgres PASSWORD 'newpassword123';
\q
```

## Once You Have the Password:

Update the `DATABASE_URL` in `backend/.env`:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/skinguard
```

Replace `YOUR_PASSWORD_HERE` with your actual password.

## Current Setting:

The `.env` file currently has:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/skinguard
```

If your password is different, please tell me and I'll update it!
