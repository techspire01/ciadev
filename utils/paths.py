import os


def _get_company_id_from_instance(instance):
    # Support models that reference either `company` or `supplier`
    company = getattr(instance, 'company', None) or getattr(instance, 'supplier', None)
    try:
        return company.id
    except Exception:
        return 'unknown'


def company_job_upload(instance, filename):
    company_id = _get_company_id_from_instance(instance)
    job_id = instance.id or "temp"
    return f"companies/{company_id}/jobs/{job_id}/{filename}"


def company_internship_upload(instance, filename):
    company_id = _get_company_id_from_instance(instance)
    intern_id = instance.id or "temp"
    return f"companies/{company_id}/internships/{intern_id}/{filename}"


def company_application_upload(instance, filename):
    # Application instance may have `job` or `internship` relation
    company = None
    if getattr(instance, 'job', None):
        company = getattr(instance.job, 'company', None) or getattr(instance.job, 'supplier', None)
    elif getattr(instance, 'internship', None):
        company = getattr(instance.internship, 'company', None) or getattr(instance.internship, 'supplier', None)

    company_id = getattr(company, 'id', 'unknown')
    application_id = instance.id or "temp"
    return f"companies/{company_id}/applications/{application_id}/{filename}"


# Global uploads
def flash_upload(instance, filename):
    return f"flash_announcements/{filename}"


def book_upload(instance, filename):
    return f"book_showcase/{filename}"


def photo_gallery_upload(instance, filename):
    return f"photo_gallery/{filename}"


def newspaper_upload(instance, filename):
    return f"newspaper_gallery/{filename}"


def supplier_logo_upload(instance, filename):
    company = getattr(instance, 'company', None) or getattr(instance, 'supplier', None)
    company_id = getattr(company, 'id', 'unknown')
    return f"companies/{company_id}/suppliers/{filename}"
