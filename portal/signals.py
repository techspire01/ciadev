"""
Signals for CIA Portal

Handles automatic file cleanup when applications or jobs are deleted.
"""

import os
import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import JobApplication, InternshipApplication, PortalJob

logger = logging.getLogger('cai_security')


@receiver(post_delete, sender=JobApplication)
def delete_job_application_files(sender, instance, **kwargs):
    """Delete uploaded files when a JobApplication is deleted"""
    files_to_delete = []
    
    if instance.resume:
        files_to_delete.append(instance.resume.name)
    if instance.additional_attachment:
        files_to_delete.append(instance.additional_attachment.name)
    
    for file_name in files_to_delete:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info("Deleted file for job application %s: %s", instance.id, file_name)
        except Exception as e:
            logger.error("Error deleting file %s: %s", file_name, str(e))


@receiver(post_delete, sender=InternshipApplication)
def delete_internship_application_files(sender, instance, **kwargs):
    """Delete uploaded files when an InternshipApplication is deleted"""
    files_to_delete = []
    
    if instance.resume:
        files_to_delete.append(instance.resume.name)
    if instance.additional_attachment:
        files_to_delete.append(instance.additional_attachment.name)
    
    for file_name in files_to_delete:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info("Deleted file for internship application %s: %s", instance.id, file_name)
        except Exception as e:
            logger.error("Error deleting file %s: %s", file_name, str(e))


@receiver(post_delete, sender=PortalJob)
def delete_job_applications_files(sender, instance, **kwargs):
    """Delete all application files when a PortalJob is deleted"""
    applications = instance.applications.all()
    for app in applications:
        if app.resume:
            try:
                file_path = os.path.join(settings.MEDIA_ROOT, app.resume.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info("Deleted resume file for job application %s when job %s was deleted", app.id, instance.id)
            except Exception as e:
                logger.error("Error deleting resume for job application %s: %s", app.id, str(e))
