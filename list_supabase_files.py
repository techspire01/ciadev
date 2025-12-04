import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from django.conf import settings
from supabase import create_client

# Initialize Supabase client
url = settings.SUPABASE_URL
key = settings.SUPABASE_SERVICE_ROLE_KEY
bucket = settings.SUPABASE_BUCKET

client = create_client(url, key)

# List all files in the bucket
try:
    files = client.storage.from_(bucket).list()
    print(f"Total files in bucket: {len(files)}")
    print("\nFiles in bucket:")
    for i, file in enumerate(files[:30]):  # Show first 30
        print(f"{i+1}. {file.get('name')} (Size: {file.get('size')} bytes)")
except Exception as e:
    print(f"Error listing files: {e}")
