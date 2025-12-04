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

# Get list of actual files in Supabase
print("Fetching actual files from Supabase...")
try:
    files = client.storage.from_(bucket).list(path='applications/resumes')
    actual_files = {f.get('name'): f for f in files}
    print(f"Found {len(actual_files)} files in Supabase:")
    for fname in actual_files.keys():
        print(f"  - {fname}")
except Exception as e:
    print(f"Error: {e}")
    exit(1)

print("\n" + "=" * 80)
print("FIXING JOB APPLICATIONS")
print("=" * 80)

bad_apps = JobApplication.objects.filter(resume__exact='applications/resumes/1.pdf')
print(f"\nFound {bad_apps.count()} job applications with bad resume path")

if bad_apps.count() > 0:
    # Get the first valid file to use as replacement
    valid_file = list(actual_files.keys())[0] if actual_files else None
    
    if valid_file:
        print(f"Fixing with: {valid_file}")
        for app in bad_apps:
            print(f"  Updating app {app.id}: {app.first_name} {app.last_name}")
            app.resume = valid_file
            app.save()
        print(f"✓ Fixed {bad_apps.count()} job applications")
    else:
        print("✗ No valid files found in Supabase to use as replacement")

print("\n" + "=" * 80)
print("FIXING INTERNSHIP APPLICATIONS")
print("=" * 80)

bad_internship_apps = InternshipApplication.objects.filter(resume__exact='applications/resumes/1.pdf')
print(f"\nFound {bad_internship_apps.count()} internship applications with bad resume path")

if bad_internship_apps.count() > 0:
    valid_file = list(actual_files.keys())[0] if actual_files else None
    
    if valid_file:
        print(f"Fixing with: {valid_file}")
        for app in bad_internship_apps:
            print(f"  Updating app {app.id}: {app.first_name} {app.last_name}")
            app.resume = valid_file
            app.save()
        print(f"✓ Fixed {bad_internship_apps.count()} internship applications")
    else:
        print("✗ No valid files found in Supabase to use as replacement")

print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

job_app_2 = JobApplication.objects.filter(id=2).first()
if job_app_2:
    print(f"\nJob Application 2:")
    print(f"  Resume path: {job_app_2.resume.name}")
    print(f"  Exists in Supabase: {job_app_2.resume.name in actual_files}")
