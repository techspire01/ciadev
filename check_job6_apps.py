import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from portal.models import JobApplication, PortalJob
from django.conf import settings

print("=" * 80)
print("JOB APPLICATIONS FOR JOB ID 6")
print("=" * 80)

# Get job 6
job = PortalJob.objects.filter(id=6).first()
if job:
    print(f"\nJob: {job.title} at {job.company_name}")
    
    apps = JobApplication.objects.filter(job=job)
    print(f"Total applications: {apps.count()}")
    
    for app in apps:
        print(f"\n  Application ID: {app.id}")
        print(f"    Name: {app.first_name} {app.last_name}")
        if app.resume:
            print(f"    Resume path: {app.resume.name}")
        else:
            print(f"    Resume: NOT SET")
else:
    print("Job ID 6 not found")
