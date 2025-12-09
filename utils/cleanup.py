import shutil
import os
import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger('django')


def delete_path(path):
    media_root = getattr(settings, 'MEDIA_ROOT', 'media')
    full_path = os.path.join(media_root, path)
    if os.path.exists(full_path):
        try:
            shutil.rmtree(full_path, ignore_errors=True)
            logger.info(f"Deleted media path: {full_path}")
        except Exception as e:
            logger.warning(f"Could not delete path {full_path}: {e}")


@receiver(post_delete)
def _generic_post_delete(sender, instance, **kwargs):
    """
    Generic hook: do nothing here. Specific receivers below handle known models.
    Kept to ensure module import registers signals cleanly.
    """
    return


try:
    from portal.models import PortalJob, PortalInternship, JobApplication, InternshipApplication
    from app.models import Supplier


    @receiver(post_delete, sender=PortalJob)
    def delete_job_folder(sender, instance, **kwargs):
        supplier = getattr(instance, 'supplier', None)
        if not supplier:
            return
        path = f"companies/{supplier.id}/jobs/{instance.id}/"
        delete_path(path)


    @receiver(post_delete, sender=PortalInternship)
    def delete_internship_folder(sender, instance, **kwargs):
        supplier = getattr(instance, 'supplier', None)
        if not supplier:
            return
        path = f"companies/{supplier.id}/internships/{instance.id}/"
        delete_path(path)


    @receiver(post_delete, sender=JobApplication)
    def delete_job_application_folder(sender, instance, **kwargs):
        if getattr(instance, 'job', None) and getattr(instance.job, 'supplier', None):
            supplier_id = instance.job.supplier.id
        elif getattr(instance, 'internship', None) and getattr(instance.internship, 'supplier', None):
            supplier_id = instance.internship.supplier.id
        else:
            supplier_id = None

        if supplier_id:
            path = f"companies/{supplier_id}/applications/{instance.id}/"
            delete_path(path)


    @receiver(post_delete, sender=InternshipApplication)
    def delete_internship_application_folder(sender, instance, **kwargs):
        if getattr(instance, 'internship', None) and getattr(instance.internship, 'supplier', None):
            supplier_id = instance.internship.supplier.id
        elif getattr(instance, 'job', None) and getattr(instance.job, 'supplier', None):
            supplier_id = instance.job.supplier.id
        else:
            supplier_id = None

        if supplier_id:
            path = f"companies/{supplier_id}/applications/{instance.id}/"
            delete_path(path)


    @receiver(post_delete, sender=Supplier)
    def delete_supplier_bucket(sender, instance, **kwargs):
        path = f"companies/{instance.id}/"
        delete_path(path)

except Exception:
    # If imports fail (during migrations or missing apps), don't break import
    logger.debug('utils.cleanup: models not available at import time.')
