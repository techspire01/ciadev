import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from portal.models import JobApplication, InternshipApplication

print("Fixing resume paths with correct full paths...")
print("=" * 80)

# Fix job applications
bad_apps = JobApplication.objects.exclude(resume__startswith='applications/resumes/')
print(f"\nJob applications without correct prefix: {bad_apps.count()}")
for app in bad_apps:
    if app.resume and app.resume.name:
        old_path = app.resume.name
        new_path = f"applications/resumes/{app.resume.name}"
        print(f"  App {app.id}: {old_path} → {new_path}")
        app.resume.name = new_path
        app.save()

# Fix internship applications  
bad_internship = InternshipApplication.objects.exclude(resume__startswith='applications/resumes/')
print(f"\nInternship applications without correct prefix: {bad_internship.count()}")
for app in bad_internship:
    if app.resume and app.resume.name:
        old_path = app.resume.name
        new_path = f"applications/resumes/{app.resume.name}"
        print(f"  App {app.id}: {old_path} → {new_path}")
        app.resume.name = new_path
        app.save()

print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

app2 = JobApplication.objects.filter(id=2).first()
if app2:
    print(f"\nJob App 2: {app2.resume.name}")
    print(f"URL: {app2.resume.url}")
