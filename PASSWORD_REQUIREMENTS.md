# Password Requirements

## Error: 422 Unprocessable Entity

If you're getting this error when creating an account, it's likely because your password doesn't meet the requirements.

## Password Must Have:

1. ✅ **At least 8 characters**
2. ✅ **At least one UPPERCASE letter** (A-Z)
3. ✅ **At least one lowercase letter** (a-z)
4. ✅ **At least one digit** (0-9)

## Examples:

### ❌ Bad Passwords:
- `password` - No uppercase, no digit
- `PASSWORD` - No lowercase, no digit
- `Password` - No digit
- `Pass123` - Only 7 characters (too short)

### ✅ Good Passwords:
- `Password123`
- `MyPass2024`
- `Secure1Pass`
- `Test1234`

## Try Again:

1. Go to http://localhost:3000
2. Use a password that meets ALL requirements above
3. Example: `Password123`
4. Create your account

It should work now! ✅
