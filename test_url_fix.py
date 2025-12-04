import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from portal.models import JobApplication
import mimetypes

# Check app 2
app = JobApplication.objects.filter(id=2).first()
if app:
    resume_url = app.resume.url
    filename = app.resume.name
    
    print(f"Resume: {filename}")
    print(f"Original URL: {resume_url}")
    
    # Auto-detect content type
    content_type, _ = mimetypes.guess_type(filename)
    print(f"Content type: {content_type}")
    
    # For PDFs, remove download parameter
    if content_type == 'application/pdf':
        if '&download=1' in resume_url:
            resume_url = resume_url.replace('&download=1', '')
        if '?download=1' in resume_url:
            resume_url = resume_url.replace('?download=1', '')
        print(f"Final URL (inline): {resume_url}")
    else:
        print(f"Final URL (download): {resume_url}")
