"""
Signals for CIA Portal

Handles automatic file cleanup when applications or jobs are deleted.
"""

import os
import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.files.storage import default_storage
from .models import JobApplication, InternshipApplication, PortalJob, PortalInternship

logger = logging.getLogger('cai_security')


@receiver(post_delete, sender=JobApplication)
def delete_job_application_files(sender, instance, **kwargs):
    """Delete uploaded files when a JobApplication is deleted"""
    files_to_delete = []
    
    if instance.resume:
        files_to_delete.append(instance.resume.name)
    if instance.additional_attachment:
        files_to_delete.append(instance.additional_attachment.name)
    
    # Delete from Supabase storage
    for file_name in files_to_delete:
        try:
            default_storage.delete(file_name)
            logger.info("Deleted file from storage for job application %s: %s", instance.id, file_name)
        except Exception as e:
            logger.error("Error deleting file %s from storage: %s", file_name, str(e))


@receiver(post_delete, sender=InternshipApplication)
def delete_internship_application_files(sender, instance, **kwargs):
    """Delete uploaded files when an InternshipApplication is deleted"""
    files_to_delete = []
    
    if instance.resume:
        files_to_delete.append(instance.resume.name)
    if instance.additional_attachment:
        files_to_delete.append(instance.additional_attachment.name)
    
    # Delete from Supabase storage
    for file_name in files_to_delete:
        try:
            default_storage.delete(file_name)
            logger.info("Deleted file from storage for internship application %s: %s", instance.id, file_name)
        except Exception as e:
            logger.error("Error deleting file %s from storage: %s", file_name, str(e))


@receiver(post_delete, sender=PortalJob)
def delete_job_applications_files(sender, instance, **kwargs):
    """Delete all application files when a PortalJob is deleted"""
    applications = instance.applications.all()
    for app in applications:
        files_to_delete = []
        if app.resume:
            files_to_delete.append(app.resume.name)
        if app.additional_attachment:
            files_to_delete.append(app.additional_attachment.name)
        
        # Delete files from Supabase storage
        for file_name in files_to_delete:
            try:
                default_storage.delete(file_name)
                logger.info("Deleted file from storage for job application %s when job %s was deleted", app.id, instance.id)
            except Exception as e:
                logger.error("Error deleting file %s from storage: %s", file_name, str(e))
    
    # Delete all applications from database (cascade handled by Django)
    logger.info("Job %s deleted with all related applications and files", instance.id)


@receiver(post_delete, sender=PortalInternship)
def delete_internship_applications_files(sender, instance, **kwargs):
    """Delete all application files when a PortalInternship is deleted"""
    applications = instance.applications.all()
    for app in applications:
        files_to_delete = []
        if app.resume:
            files_to_delete.append(app.resume.name)
        if app.additional_attachment:
            files_to_delete.append(app.additional_attachment.name)
        
        # Delete files from Supabase storage
        for file_name in files_to_delete:
            try:
                default_storage.delete(file_name)
                logger.info("Deleted file from storage for internship application %s when internship %s was deleted", app.id, instance.id)
            except Exception as e:
                logger.error("Error deleting file %s from storage: %s", file_name, str(e))
    
    # Delete all applications from database (cascade handled by Django)
    logger.info("Internship %s deleted with all related applications and files", instance.id)
