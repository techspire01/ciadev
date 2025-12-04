import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from portal.models import JobApplication, InternshipApplication

# Check application ID 3
job_app = JobApplication.objects.filter(id=3).first()
internship_app = InternshipApplication.objects.filter(id=3).first()

if job_app:
    print(f"Job Application ID 3 found")
    print(f"Resume name: {job_app.resume.name}")
    print(f"Resume exists: {bool(job_app.resume)}")
    print(f"Resume storage: {job_app.resume.storage if job_app.resume else 'N/A'}")
elif internship_app:
    print(f"Internship Application ID 3 found")
    print(f"Resume name: {internship_app.resume.name}")
    print(f"Resume exists: {bool(internship_app.resume)}")
else:
    print("Application not found")
