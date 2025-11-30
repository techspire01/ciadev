from django.db import models

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
