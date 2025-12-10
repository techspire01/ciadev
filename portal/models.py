from django.db import models
from django.core.validators import FileExtensionValidator
from app.models import Supplier
from utils.paths import (
    company_application_upload,
    company_job_upload,
    company_internship_upload,
)

# Create your models here.

class PortalInternship(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.CharField(max_length=255)
    posted_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    company_name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to=company_internship_upload, null=True, blank=True)
    image_url = models.URLField(blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True, related_name='internships')
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
    company_name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to=company_job_upload, null=True, blank=True)
    image_url = models.URLField(blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True, related_name='jobs')
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
    STATUS_CHOICES = [
        ('fresher', 'Fresher'),
        ('experienced', 'Experienced'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    # Experience Status
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='fresher')

    # Resume Upload
    resume = models.FileField(
        upload_to=company_application_upload,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text='Max size: 2MB. Accepted formats: PDF, DOCX, DOC'
    )

    # Education Details (Required for all)
    school_name = models.CharField(max_length=255, blank=True, default='')
    city_of_study = models.CharField(max_length=255, blank=True, default='')
    degree = models.CharField(max_length=255, blank=True, default='')
    field_of_study = models.CharField(max_length=255, blank=True, default='')
    study_from_date = models.DateField(blank=True, null=True)
    study_to_date = models.DateField(blank=True, null=True)
    currently_studying = models.BooleanField(default=False)

    # Skills (Optional, for clarity)
    skills = models.TextField(blank=True, help_text='Enter skills separated by commas or as tags')

    # LinkedIn Profile
    linkedin_profile = models.URLField(blank=True)

    # Internships (Optional for freshers)
    internships = models.TextField(blank=True, help_text='Details of internships (optional)')

    # Work Experience (For experienced applicants only)
    # Using JSONField to store multiple work experience entries
    work_experiences = models.JSONField(default=list, blank=True, help_text='Array of work experience entries')

    # Additional Questions
    additional_questions = models.TextField(blank=True, max_length=2000)

    # Message to Hiring Manager
    message_to_manager = models.TextField(blank=True, max_length=2000)

    # Additional Attachments (Optional)
    additional_attachment = models.FileField(
        upload_to=company_application_upload,
        blank=True,
        null=True,
        help_text='Max size: 5MB. Accepted formats: PDF, DOCX, DOC, PNG, JPG'
    )

    # Metadata
    applied_date = models.DateTimeField(auto_now_add=True)
    internship = models.ForeignKey(PortalInternship, on_delete=models.CASCADE, related_name='applications')
    supplier = models.ForeignKey('app.Supplier', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.internship.title}"

    def delete(self, *args, **kwargs):
        """
        Override model delete to remove resume and additional_attachment from configured storage.
        """
        resume_name = self.resume.name if self.resume else None
        attachment_name = self.additional_attachment.name if self.additional_attachment else None
        super().delete(*args, **kwargs)  # remove DB record
        # After DB delete, remove storage objects
        try:
            from django.core.files.storage import default_storage
            if resume_name:
                default_storage.delete(resume_name)
            if attachment_name:
                default_storage.delete(attachment_name)
        except Exception:
            pass

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('fresher', 'Fresher'),
        ('experienced', 'Experienced'),
    ]

    EMPLOYMENT_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    # Experience Status
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='fresher')

    # Resume Upload
    resume = models.FileField(
        upload_to=company_application_upload,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text='Max size: 2MB. Accepted formats: PDF, DOCX, DOC'
    )

    # Education Details (Required for all applicants)
    school_name = models.CharField(max_length=255, blank=True, default='')
    city_of_study = models.CharField(max_length=255, blank=True, default='')
    degree = models.CharField(max_length=255, blank=True, default='')
    field_of_study = models.CharField(max_length=255, blank=True, default='')
    study_from_date = models.DateField(blank=True, null=True)
    study_to_date = models.DateField(blank=True, null=True)
    currently_studying = models.BooleanField(default=False)

    # Work Experience (at least 1 entry required for experienced applicants)
    # Using JSONField to store multiple work experience entries
    work_experiences = models.JSONField(
        default=list,
        blank=True,
        help_text='Array of work experience entries (required for experienced applicants)'
    )

    # Skills
    skills = models.TextField(blank=True, help_text='Enter skills separated by commas or as tags')

    # LinkedIn Profile
    linkedin_profile = models.URLField(blank=True)

    # Screening Questions (Optional)
    screening_questions = models.TextField(blank=True, max_length=2000)

    # Message to Hiring Manager
    message_to_manager = models.TextField(blank=True, max_length=2000)

    # Additional Attachments (Optional)
    additional_attachment = models.FileField(
        upload_to=company_application_upload,
        blank=True,
        null=True,
        help_text='Max size: 5MB. Accepted formats: PDF, DOCX, DOC, PNG, JPG'
    )

    # Metadata
    applied_date = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(PortalJob, on_delete=models.CASCADE, related_name='applications')
    supplier = models.ForeignKey('app.Supplier', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job.title}"

    def delete(self, *args, **kwargs):
        """
        Override model delete to remove resume and additional_attachment from configured storage.
        """
        resume_name = self.resume.name if self.resume else None
        attachment_name = self.additional_attachment.name if self.additional_attachment else None
        super().delete(*args, **kwargs)  # remove DB record
        # After DB delete, remove storage objects
        try:
            from django.core.files.storage import default_storage
            if resume_name:
                default_storage.delete(resume_name)
            if attachment_name:
                default_storage.delete(attachment_name)
        except Exception:
            pass
