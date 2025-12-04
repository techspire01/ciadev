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

print("Listing all files in bucket recursively:")
print("=" * 80)

def list_files_recursive(path='', depth=0):
    indent = "  " * depth
    try:
        items = client.storage.from_(bucket).list(path=path)
        for item in items:
            name = item.get('name')
            is_dir = item.get('id') is None  # Directories have no id
            
            if is_dir:
                print(f"{indent}📁 {name}/")
                list_files_recursive(path=f"{path}{name}/" if path else f"{name}/", depth=depth+1)
            else:
                size = item.get('size', 0)
                print(f"{indent}📄 {name} ({size} bytes)")
    except Exception as e:
        print(f"{indent}❌ Error: {e}")

list_files_recursive()
