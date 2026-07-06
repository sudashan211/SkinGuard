import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"SUPABASE_URL: {url}")
print(f"Service Role Key Length: {len(key) if key else 0}")
print(f"Key starts with: {key[:20] if key else 'None'}...")

if url and key and len(key) > 100:
    print("\n✅ Credentials look valid!")
else:
    print("\n❌ Credentials are missing or invalid")