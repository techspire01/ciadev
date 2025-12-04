import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from portal.models import JobApplication
from django.conf import settings
import mimetypes

app = JobApplication.objects.filter(id=2).first()
if app:
    filename = app.resume.name
    content_type, _ = mimetypes.guess_type(filename)
    
    # Build direct public URL
    resume_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{filename}"
    
    print(f"Filename: {filename}")
    print(f"Content-Type: {content_type}")
    print(f"\nDirect Public URL (for PDFs):")
    print(f"  {resume_url}")
    
    if content_type != 'application/pdf':
        print(f"\nURL with download (for non-PDFs):")
        print(f"  {resume_url}?download=1")
