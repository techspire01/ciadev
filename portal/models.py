from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.

class PortalInternship(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.CharField(max_length=255)
    posted_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    company_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    salary = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'portal_internship'
        managed = True  # Let Django manage this table

    def __str__(self):
        return f"{self.title} at {self.company_name}"

class PortalJob(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    posted_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    company_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    salary = models.CharField(max_length=100)
    experience = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'portal_job'
        managed = True  # Let Django manage this table

    def __str__(self):
        return f"{self.title} at {self.company_name}"

class InternshipApplication(models.Model):
    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    # Education & Skills
    education = models.CharField(max_length=100, choices=[
        ('high_school', 'High School'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Postgraduate'),
    ])
    major = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True)

    # Internship Preferences
    preferred_role = models.CharField(max_length=255, blank=True)
    availability = models.CharField(max_length=50, choices=[
        ('full_time', 'Full-time (40 hours/week)'),
        ('part_time', 'Part-time (20-30 hours/week)'),
        ('flexible', 'Flexible'),
    ])
    duration = models.CharField(max_length=50, choices=[
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('9_months', '9 Months'),
        ('12_months', '12 Months'),
    ], blank=True)
    start_date = models.DateField(blank=True, null=True)

    # Documents
    resume = models.FileField(
        upload_to='applications/resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    cover_letter = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)

    # Metadata
    applied_date = models.DateTimeField(auto_now_add=True)
    internship = models.ForeignKey(PortalInternship, on_delete=models.CASCADE, related_name='applications')

    def __str__(self):
        return f"{self.full_name} - {self.internship.title}"

class JobApplication(models.Model):
    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    # Education & Experience
    education = models.CharField(max_length=100, choices=[
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('phd', 'PhD'),
    ])
    major = models.CharField(max_length=255, blank=True)
    experience_years = models.CharField(max_length=50, choices=[
        ('0', '0 years (Entry Level)'),
        ('1-2', '1-2 years'),
        ('3-5', '3-5 years'),
        ('6-10', '6-10 years'),
        ('10+', '10+ years'),
    ])
    current_position = models.CharField(max_length=255, blank=True)
    current_company = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True)

    # Job Preferences
    preferred_role = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(max_length=50, choices=[
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
    ])
    salary_expectation = models.CharField(max_length=100, blank=True)
    availability_date = models.DateField(blank=True, null=True)
    work_authorization = models.CharField(max_length=100, choices=[
        ('us_citizen', 'US Citizen'),
        ('permanent_resident', 'Permanent Resident'),
        ('h1b', 'H1B Visa'),
        ('tn_visa', 'TN Visa'),
        ('other_visa', 'Other Visa'),
        ('need_sponsorship', 'Require Sponsorship'),
    ])

    # Documents
    resume = models.FileField(
        upload_to='applications/resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    cover_letter = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    additional_info = models.TextField(blank=True)

    # Metadata
    applied_date = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(PortalJob, on_delete=models.CASCADE, related_name='applications')

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"
