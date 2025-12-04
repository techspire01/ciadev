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
    
    # Try to get the URL
    try:
        url = app.resume.url
        print(f"URL from storage: {url}")
    except Exception as e:
        print(f"Error from storage backend: {e}")
        # Fallback URL
        fallback_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{app.resume.name}"
        print(f"Fallback URL: {fallback_url}")
        
        # For PDF, remove download parameter
        if app.resume.name.endswith('.pdf'):
            if '&download=1' in fallback_url:
                fallback_url = fallback_url.replace('&download=1', '')
            print(f"URL for inline PDF: {fallback_url}")
else:
    print("Application or resume not found")
