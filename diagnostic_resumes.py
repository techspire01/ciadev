import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from portal.models import JobApplication, InternshipApplication
from django.conf import settings
from supabase import create_client

# Initialize Supabase client
url = settings.SUPABASE_URL
key = settings.SUPABASE_SERVICE_ROLE_KEY
bucket = settings.SUPABASE_BUCKET

client = create_client(url, key)

print("=" * 80)
print("CHECKING JOB APPLICATIONS")
print("=" * 80)

job_apps = JobApplication.objects.all()[:5]
for app in job_apps:
    print(f"\nApplication ID: {app.id}")
    print(f"  Name: {app.first_name} {app.last_name}")
    if app.resume:
        print(f"  Resume path in DB: {app.resume.name}")
        
        # Check if file exists in Supabase
        try:
            result = client.storage.from_(bucket).list(path='applications/resumes')
            files = [f.get('name') for f in result]
            print(f"  Files in applications/resumes: {files}")
        except Exception as e:
            print(f"  Error listing files: {e}")
    else:
        print(f"  Resume: NOT SET")

print("\n" + "=" * 80)
print("CHECKING INTERNSHIP APPLICATIONS")
print("=" * 80)

internship_apps = InternshipApplication.objects.all()[:5]
for app in internship_apps:
    print(f"\nApplication ID: {app.id}")
    print(f"  Name: {app.first_name} {app.last_name}")
    if app.resume:
        print(f"  Resume path in DB: {app.resume.name}")
    else:
        print(f"  Resume: NOT SET")
