import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from portal.models import JobApplication
from django.conf import settings

# Check app 2
app = JobApplication.objects.filter(id=2).first()
if app:
    print(f"Application 2:")
    print(f"  Resume name: {app.resume.name}")
    
    # Build the correct URL
    url_correct = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{app.resume.name}"
    print(f"\nCorrect URL: {url_correct}")
    
    # Try getting from storage
    try:
        storage_url = app.resume.url
        print(f"Storage URL: {storage_url}")
    except Exception as e:
        print(f"Storage error: {e}")
