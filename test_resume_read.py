import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from portal.models import JobApplication
from django.conf import settings

# Get application ID 3
app = JobApplication.objects.filter(id=3).first()

if app and app.resume:
    print(f"Resume name: {app.resume.name}")
    
    # Try to check if file exists
    try:
        exists = app.resume.storage.exists(app.resume.name)
        print(f"File exists in Supabase: {exists}")
    except Exception as e:
        print(f"Error checking existence: {e}")
    
    # Try to open and read the file
    try:
        file_obj = app.resume.open('rb')
        data = file_obj.read()
        file_obj.close()
        print(f"Successfully read file. Size: {len(data)} bytes")
    except Exception as e:
        print(f"Error opening/reading file: {e}")
        print(f"Error type: {type(e).__name__}")
else:
    print("Application or resume not found")
