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

# List files in applications/resumes folder
try:
    files = client.storage.from_(bucket).list(path='applications/resumes')
    print(f"Files in applications/resumes: {len(files)}")
    print("\nFiles:")
    for i, file in enumerate(files):
        print(f"{i+1}. {file.get('name')} (Size: {file.get('size')} bytes)")
except Exception as e:
    print(f"Error listing files: {e}")

print("\n" + "="*50)
# Also list root to see structure
try:
    files = client.storage.from_(bucket).list(path='applications')
    print(f"Files in applications: {len(files)}")
    print("\nContents:")
    for i, file in enumerate(files):
        print(f"{i+1}. {file.get('name')} (Size: {file.get('size')} bytes)")
except Exception as e:
    print(f"Error listing files: {e}")
