from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404, FileResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import json
import os
import logging
from .models import PortalInternship, PortalJob, InternshipApplication, JobApplication
from app.models import Supplier
from app.utils import get_supplier_for_user_or_raise
import mimetypes
from io import BytesIO

logger = logging.getLogger('cai_security')

# Try to import ratelimit, provide fallback if not installed
try:
    from ratelimit.decorators import ratelimit
except ImportError:
    # Fallback: create a no-op decorator if ratelimit is not installed
    def ratelimit(key=None, rate=None, method=None, block=False):
        def decorator(func):
            return func
        return decorator

# Create your views here.


def details(request):
    """Opportunity details page"""
    vacancy_id = request.GET.get('id')
    vacancy_type = request.GET.get('type')
    
    vacancy = None
    try:
        if vacancy_type == 'internship':
            vacancy = get_object_or_404(PortalInternship, id=vacancy_id)
        elif vacancy_type == 'job':
            vacancy = get_object_or_404(PortalJob, id=vacancy_id)
        else:
            raise Http404("Vacancy type not specified")
    except Http404:
        # Render a "not found" page or redirect
        return render(request, 'brand_new_site/details.html', {'vacancy': None})
    except Exception as e:
        # Log the exception and render a generic error page
        # In a real app, you'd use proper logging
        return render(request, 'brand_new_site/details.html', {'vacancy': None})


    return render(request, 'brand_new_site/details.html', {'vacancy': vacancy})


def brand_new_site_dashboard(request):
    """Render the brand new site dashboard - shows all active jobs/internships from all companies"""
    try:
        # Get filter and location from query parameters
        current_filter = request.GET.get('filter', 'all')
        selected_location = request.GET.get('location', '')

        # Base querysets
        # Order by posted_date descending so newest appear first
        internships_query = PortalInternship.objects.filter(is_active=True).order_by('-posted_date')
        jobs_query = PortalJob.objects.filter(is_active=True).order_by('-posted_date')

        # Apply location filter
        if selected_location:
            internships_query = internships_query.filter(location__icontains=selected_location)
            jobs_query = jobs_query.filter(location__icontains=selected_location)

        # Apply type filter
        if current_filter == 'internship':
            jobs_query = jobs_query.none()
        elif current_filter == 'job':
            internships_query = internships_query.none()

        internships = list(internships_query)
        jobs = list(jobs_query)

        vacancies = []

        # Include posted_date in the dict for sorting, then remove/keep as needed
        for internship in internships:
            vacancies.append({
                'id': internship.id,
                'role': internship.title,
                'company_name': internship.supplier.name if internship.supplier else internship.company_name,
                'package': internship.salary,
                'job_description': internship.description,
                'type': 'internship',
                'requirements': internship.requirements,
                'duration': internship.duration,
                'location': internship.location,
                'posted_date': getattr(internship, 'posted_date', None)
            })

        for job in jobs:
            vacancies.append({
                'id': job.id,
                'role': job.title,
                'company_name': job.supplier.name if job.supplier else job.company_name,
                'package': job.salary,
                'job_description': job.description,
                'type': 'job',
                'requirements': job.requirements,
                'location': job.location,
                'experience': job.experience,
                'posted_date': getattr(job, 'posted_date', None)
            })

        # Sort combined vacancies by posted_date descending (newest first). None dates go last.
        vacancies.sort(key=lambda v: v.get('posted_date') or 0, reverse=True)

        # Collect unique locations from all active internships and jobs for the dropdown
        all_internships = PortalInternship.objects.filter(is_active=True)
        all_jobs = PortalJob.objects.filter(is_active=True)
        locations = set()
        for internship in all_internships:
            if internship.location:
                locations.add(internship.location.strip())
        for job in all_jobs:
            if job.location:
                locations.add(job.location.strip())

        # Sort locations alphabetically
        unique_locations = sorted(list(locations))

        context = {
            'vacancies': vacancies, 
            'locations': unique_locations,
            'current_filter': current_filter,
            'selected_location': selected_location
        }
    except Exception as e:
        # In a real app, you'd use proper logging
        context = {'vacancies': [], 'locations': [], 'error': str(e)}

    return render(request, 'brand_new_site/dashboard.html', context)


def supplier_required(view_func):
    """
    Decorator to check if user is a supplier and attach supplier to request.
    
    Uses new OneToOne relationship first, falls back to email lookup for migration window.
    """
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            supplier = get_supplier_for_user_or_raise(request)
            request.supplier = supplier  # Attach supplier to request for downstream use
            return view_func(request, *args, **kwargs)
        except PermissionDenied:
            raise
    return _wrapped_view


def protected_media(request, path):
    """
    Protected endpoint for downloading files (resumes, attachments).
    
    Validates ownership before serving files.
    Only staff or application owner can access.
    """
    try:
        # Sanitize path to prevent directory traversal
        safe_path = os.path.normpath(path).lstrip(os.sep)
        file_path = os.path.join(settings.MEDIA_ROOT, safe_path)
        
        # Verify file exists
        if not os.path.exists(file_path):
            logger.warning("Attempt to access non-existent file: %s by user %s", path, request.user)
            raise Http404("File not found.")
        
        # Staff members can access any file
        if request.user.is_staff:
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        
        # Find application referencing this file
        job_app = JobApplication.objects.filter(resume__contains=safe_path).first()
        if not job_app:
            job_app = JobApplication.objects.filter(additional_attachment__contains=safe_path).first()
        
        if not job_app:
            internship_app = InternshipApplication.objects.filter(resume__contains=safe_path).first()
            if not internship_app:
                internship_app = InternshipApplication.objects.filter(additional_attachment__contains=safe_path).first()
        
        # Check ownership
        if job_app:
            app = job_app
        elif internship_app:
            app = internship_app
        else:
            logger.warning("Attempt to access file with no application reference: %s by user %s", path, request.user)
            raise Http404("File not found.")
        
        # Verify user is logged in and owns the application
        if not request.user.is_authenticated:
            logger.warning("Unauthenticated access attempt to protected media: %s", path)
            return HttpResponseForbidden("Authentication required.")
        
        # Check if user is the supplier who posted the job/internship
        if app.supplier and app.supplier.user_id == request.user.id:
            logger.info("Protected media access granted to supplier %s for file %s", request.user.id, path)
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        
        # Also allow if supplier user is matched by email (migration window)
        if app.supplier and app.supplier.email and app.supplier.email.lower() == request.user.email.lower():
            logger.info("Protected media access granted to supplier (by email) %s for file %s", request.user.email, path)
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        
        logger.warning("Unauthorized media access attempt by %s for %s (application supplier: %s)", 
                      request.user.email, path, app.supplier.email if app.supplier else "None")
        return HttpResponseForbidden("You do not have permission to access this file.")
    
    except Http404:
        raise
    except Exception as e:
        logger.error("Error in protected_media: %s", str(e))
        raise Http404("Error accessing file.")


@supplier_required
def job_portal_admin(request):
    """Render the job portal admin dashboard with optimized queries"""
    try:
        supplier = request.supplier  # Use supplier attached by decorator
        
        # Filter by supplier - only show this company's postings
        internships = PortalInternship.objects.filter(supplier=supplier).order_by('-posted_date')
        jobs = PortalJob.objects.filter(supplier=supplier).order_by('-posted_date')
        
        # Fetch applications for this supplier's postings
        internship_applications = InternshipApplication.objects.filter(supplier=supplier).order_by('-applied_date')
        job_applications = JobApplication.objects.filter(supplier=supplier).order_by('-applied_date')
        
        # Use annotate instead of N+1 count() queries
        from django.db.models import Count
        internships = internships.annotate(application_count=Count('applications'))
        jobs = jobs.annotate(application_count=Count('applications'))
        
    except PermissionDenied:
        raise

    return render(request, 'brand_new_site/job_portal_admin.html', {
        'internships': internships,
        'jobs': jobs,
        'internship_applications': internship_applications,
        'job_applications': job_applications,
    })

def job_admin(request):
    """Render the job admin UI model page"""
    return render(request, 'brand_new_site/job_admin.html')

# API Endpoints for Internship Management
# Temporarily disable CSRF for testing - remove @csrf_exempt in production

@csrf_exempt
@require_POST
def add_internship(request):
    """Add a new internship via AJAX"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        data = json.loads(request.body)
        internship = PortalInternship.objects.create(
            title=data['title'],
            supplier=supplier,
            duration=data.get('duration', ''),
            salary=data.get('stipend', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            requirements=data.get('requirements', ''),
            responsibilities=data.get('responsibilities', '')
        )
        logger.info("Internship created: %s by supplier %s", internship.id, supplier.id)
        return JsonResponse({
            'success': True,
            'id': internship.id,
            'message': 'Internship added successfully!'
        })
    except PermissionDenied as e:
        logger.warning("Permission denied for add_internship: %s", str(e))
        return JsonResponse({'success': False, 'message': str(e)}, status=403)
    except Exception as e:
        logger.error("Error in add_internship: %s", str(e))
        return JsonResponse({'success': False, 'message': str(e)})

@require_GET
def get_internships(request):
    """Get all internships for the admin view"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        internships = PortalInternship.objects.filter(supplier=supplier).order_by('-posted_date')
    except PermissionDenied:
        internships = PortalInternship.objects.none()
    
    data = []
    for internship in internships:
        data.append({
            'id': internship.id,
            'role': internship.title,
            'company': internship.company_name,
            'duration': internship.duration,
            'stipend': internship.salary,
            'description': internship.description,
            'email': internship.email,
            'requirements': internship.requirements,
            'responsibilities': internship.responsibilities,
            'location': internship.location,
            'is_active': internship.is_active,
            'posted_date': internship.posted_date.strftime('%Y-%m-%d')
        })
    return JsonResponse({'success': True, 'internships': data})

@csrf_exempt
@require_POST
def update_internship(request, internship_id):
    """Update an existing internship"""
    try:
        internship = get_object_or_404(PortalInternship, id=internship_id)
        
        # Check ownership
        supplier = get_supplier_for_user_or_raise(request)
        if internship.supplier != supplier:
            logger.warning("Unauthorized internship update attempt by user %s for internship %s", request.user.id, internship_id)
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        data = json.loads(request.body)

        internship.title = data.get('title', internship.title)
        internship.company_name = data.get('company', internship.company_name)
        internship.duration = data.get('duration', internship.duration)
        internship.salary = data.get('stipend', internship.salary)
        internship.description = data.get('description', internship.description)
        internship.email = data.get('email', internship.email)
        internship.requirements = data.get('requirements', internship.requirements)
        internship.responsibilities = data.get('responsibilities', internship.responsibilities)
        internship.location = data.get('location', internship.location)
        internship.save()

        logger.info("Internship %s updated by supplier %s", internship_id, supplier.id)
        return JsonResponse({
            'success': True,
            'message': 'Internship updated successfully!'
        })
    except PermissionDenied:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def toggle_internship_status(request, internship_id):
    """Toggle internship active status (pause/resume)"""
    try:
        internship = get_object_or_404(PortalInternship, id=internship_id)
        
        # Check ownership
        supplier = get_supplier_for_user_or_raise(request)
        if internship.supplier != supplier:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        internship.is_active = not internship.is_active
        internship.save()

        status = 'resumed' if internship.is_active else 'paused'
        return JsonResponse({
            'success': True,
            'message': f'Internship {status} successfully!',
            'is_active': internship.is_active
        })
    except PermissionDenied:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def delete_internship_api(request, internship_id):
    """Delete an internship via API"""
    try:
        internship = get_object_or_404(PortalInternship, id=internship_id)
        
        # Check ownership
        supplier = get_supplier_for_user_or_raise(request)
        if internship.supplier != supplier:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        # Get count of applications before deletion
        app_count = internship.applications.count()
        internship_title = internship.title
        
        # Delete internship (cascades to applications and files)
        internship.delete()
        
        logger.info(f"API: Internship '{internship_title}' (ID: {internship_id}) deleted with {app_count} related applications")
        return JsonResponse({
            'success': True,
            'message': f'Internship deleted successfully! ({app_count} applications and all files removed)'
        })
    except PermissionDenied:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        logger.error(f"Error deleting internship: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def add_job_api(request):
    """Add a new job via AJAX"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        data = json.loads(request.body)
        job = PortalJob.objects.create(
            title=data['title'],
            supplier=supplier,
            company_name=data['company'],
            location=data.get('location', ''),
            salary=data.get('salary', ''),
            description=data.get('description', ''),
            email=data.get('email', ''),
            requirements=data.get('requirements', ''),
            responsibilities=data.get('responsibilities', ''),
            experience=data.get('experience', '')
        )
        return JsonResponse({
            'success': True,
            'id': job.id,
            'message': 'Job added successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def update_job_api(request, job_id):
    """Update an existing job via API"""
    try:
        job = get_object_or_404(PortalJob, id=job_id)
        
        # Check ownership
        supplier = get_supplier_for_user_or_raise(request)
        if job.supplier != supplier:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        data = json.loads(request.body)

        job.title = data.get('title', job.title)
        job.company_name = data.get('company', job.company_name)
        job.location = data.get('location', job.location)
        job.salary = data.get('salary', job.salary)
        job.description = data.get('description', job.description)
        job.email = data.get('email', job.email)
        job.requirements = data.get('requirements', job.requirements)
        job.responsibilities = data.get('responsibilities', job.responsibilities)
        job.experience = data.get('experience', job.experience)
        job.save()

        return JsonResponse({
            'success': True,
            'message': 'Job updated successfully!'
        })
    except PermissionDenied:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def toggle_job_status_api(request, job_id):
    """Toggle job active status (pause/resume) via API"""
    try:
        job = get_object_or_404(PortalJob, id=job_id)
        
        # Check ownership
        supplier = get_supplier_for_user_or_raise(request)
        if job.supplier != supplier:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        job.is_active = not job.is_active
        job.save()

        status = 'resumed' if job.is_active else 'paused'
        return JsonResponse({
            'success': True,
            'message': f'Job {status} successfully!',
            'is_active': job.is_active
        })
    except PermissionDenied:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def delete_job_api(request, job_id):
    """Delete a job via API"""
    try:
        job = get_object_or_404(PortalJob, id=job_id)
        
        # Check ownership
        supplier = get_supplier_for_user_or_raise(request)
        if job.supplier != supplier:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        # Get count of applications before deletion
        app_count = job.applications.count()
        job_title = job.title
        
        # Delete job (cascades to applications and files)
        job.delete()
        
        logger.info(f"API: Job '{job_title}' (ID: {job_id}) deleted with {app_count} related applications")
        return JsonResponse({
            'success': True,
            'message': f'Job deleted successfully! ({app_count} applications and all files removed)'
        })
    except PermissionDenied:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        logger.error(f"Error deleting job: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})

# Server-side views for internship management
@login_required
def edit_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    
    # Check if user owns this internship
    try:
        supplier = get_supplier_for_user_or_raise(request)
        if internship.supplier != supplier:
            raise PermissionDenied("You do not have permission to edit this internship.")
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can edit internships.")

    if request.method == 'POST':
        internship.title = request.POST.get('title')
        internship.company_name = request.POST.get('company')
        internship.duration = request.POST.get('duration')
        internship.salary = request.POST.get('stipend')
        internship.email = request.POST.get('email')
        internship.description = request.POST.get('description')
        internship.requirements = request.POST.get('requirements')
        internship.responsibilities = request.POST.get('responsibilities')
        internship.location = request.POST.get('location')
        internship.save()
        return redirect('job_portal_admin')

    return redirect('job_portal_admin')

@login_required
def delete_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    
    # Check if user owns this internship
    try:
        supplier = get_supplier_for_user_or_raise(request)
        if internship.supplier != supplier:
            raise PermissionDenied("You do not have permission to delete this internship.")
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can delete internships.")
    
    # Get count of applications before deletion for logging
    app_count = internship.applications.count()
    internship_title = internship.title
    
    # Delete internship (cascades to applications and files)
    internship.delete()
    
    logger.info(f"Internship '{internship_title}' (ID: {id}) deleted with {app_count} related applications and their files")
    messages.success(request, f"Internship deleted successfully! ({app_count} applications and all files removed)")
    return redirect('job_portal_admin')

@login_required
def toggle_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    
    # Check if user owns this internship
    try:
        supplier = get_supplier_for_user_or_raise(request)
        if internship.supplier != supplier:
            raise PermissionDenied("You do not have permission to toggle this internship.")
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can toggle internships.")
    
    internship.is_active = not internship.is_active
    internship.save()
    return redirect('job_portal_admin')

# Server-side views for job management
@login_required
def edit_job(request, id):
    job = get_object_or_404(PortalJob, id=id)
    
    # Check if user owns this job
    try:
        supplier = get_supplier_for_user_or_raise(request)
        if job.supplier != supplier:
            raise PermissionDenied("You do not have permission to edit this job.")
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can edit jobs.")

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.company_name = request.POST.get('company')
        job.location = request.POST.get('location')
        job.salary = request.POST.get('salary')
        job.email = request.POST.get('email')
        job.description = request.POST.get('description')
        job.requirements = request.POST.get('requirements')
        job.responsibilities = request.POST.get('responsibilities')
        job.experience = request.POST.get('experience')
        job.save()
        return redirect('job_portal_admin')

    return redirect('job_portal_admin')

@login_required
def delete_job(request, id):
    job = get_object_or_404(PortalJob, id=id)
    
    # Check if user owns this job
    try:
        supplier = get_supplier_for_user_or_raise(request)
        if job.supplier != supplier:
            raise PermissionDenied("You do not have permission to delete this job.")
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can delete jobs.")
    
    # Get count of applications before deletion for logging
    app_count = job.applications.count()
    job_title = job.title
    
    # Delete job (cascades to applications and files)
    job.delete()
    
    logger.info(f"Job '{job_title}' (ID: {id}) deleted with {app_count} related applications and their files")
    messages.success(request, f"Job deleted successfully! ({app_count} applications and all files removed)")
    return redirect('job_portal_admin')

@login_required
def toggle_job(request, id):
    job = get_object_or_404(PortalJob, id=id)
    
    # Check if user owns this job
    try:
        supplier = get_supplier_for_user_or_raise(request)
        if job.supplier != supplier:
            raise PermissionDenied("You do not have permission to toggle this job.")
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can toggle jobs.")
    
    job.is_active = not job.is_active
    job.save()
    return redirect('job_portal_admin')

@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def internship_application(request, internship_id):
    """Handle internship application form with rate-limiting"""
    from .forms import InternshipApplicationForm
    
    internship = get_object_or_404(PortalInternship, id=internship_id, is_active=True)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = InternshipApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.internship = internship
                application.supplier = internship.supplier
                application.save()
                logger.info("Internship application submitted successfully for internship %s by %s", 
                           internship_id, request.META.get('REMOTE_ADDR'))
                if is_ajax:
                    return JsonResponse({'status': 'success', 'message': 'Your internship application has been submitted successfully!'})
                messages.success(request, 'Your internship application has been submitted successfully!')
                return redirect('dashboard')
            except Exception as e:
                logger.error("Error submitting internship application: %s", str(e))
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': f'Error submitting application: {str(e)}'})
                messages.error(request, f'Error submitting application: {str(e)}')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f'{field}: {error}')
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Please correct the errors: ' + ', '.join(error_messages)})
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = InternshipApplicationForm()

    context = {
        'internship': internship,
        'form': form
    }
    return render(request, 'brand_new_site/internship_application.html', context)

@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def job_application(request, job_id):
    """Handle job application form with rate-limiting"""
    from .forms import JobApplicationForm
    import json
    
    job = get_object_or_404(PortalJob, id=job_id, is_active=True)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.job = job
                application.supplier = job.supplier
                application.save()
                logger.info("Job application submitted successfully for job %s by %s", 
                           job_id, request.META.get('REMOTE_ADDR'))
                if is_ajax:
                    return JsonResponse({'status': 'success', 'message': 'Your job application has been submitted successfully!'})
                messages.success(request, 'Your job application has been submitted successfully!')
                return redirect('dashboard')
            except Exception as e:
                logger.error("Error submitting job application: %s", str(e))
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': f'Error submitting application: {str(e)}'})
                messages.error(request, f'Error submitting application: {str(e)}')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f'{field}: {error}')
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Please correct the errors: ' + ', '.join(error_messages)})
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = JobApplicationForm()

    context = {
        'job': job,
        'form': form
    }
    return render(request, 'brand_new_site/job_application.html', context)


@supplier_required
def view_job_applicants(request, job_id):
    """View all applicants for a specific job - ONLY for the employer who posted it"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        
        # Get the job and verify the supplier owns it
        job = get_object_or_404(PortalJob, id=job_id, supplier=supplier)
        
        # Get applications for this job
        applications_list = JobApplication.objects.filter(job=job).order_by('-applied_date')
        
        # Paginate results - 10 applicants per page
        paginator = Paginator(applications_list, 10)
        page = request.GET.get('page', 1)
        
        try:
            applications = paginator.page(page)
        except PageNotAnInteger:
            applications = paginator.page(1)
        except EmptyPage:
            applications = paginator.page(paginator.num_pages)
        
        context = {
            'job': job,
            'applications': applications,
            'type': 'job',
            'paginator': paginator,
            'page_obj': applications
        }
        return render(request, 'brand_new_site/applicants_list.html', context)
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def view_internship_applicants(request, internship_id):
    """View all applicants for a specific internship - ONLY for the employer who posted it"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        
        # Get the internship and verify the supplier owns it
        internship = get_object_or_404(PortalInternship, id=internship_id, supplier=supplier)
        
        # Get applications for this internship
        applications_list = InternshipApplication.objects.filter(internship=internship).order_by('-applied_date')
        
        # Paginate results - 10 applicants per page
        paginator = Paginator(applications_list, 10)
        page = request.GET.get('page', 1)
        
        try:
            applications = paginator.page(page)
        except PageNotAnInteger:
            applications = paginator.page(1)
        except EmptyPage:
            applications = paginator.page(paginator.num_pages)
        
        context = {
            'internship': internship,
            'applications': applications,
            'type': 'internship',
            'paginator': paginator,
            'page_obj': applications
        }
        return render(request, 'brand_new_site/applicants_list.html', context)
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def view_job_applicant_detail(request, job_id, application_id):
    """View details of a specific job applicant - ONLY for the employer who posted it"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        
        # Get the job and verify the supplier owns it
        job = get_object_or_404(PortalJob, id=job_id, supplier=supplier)
        
        # Get the application and verify it belongs to this job
        application = get_object_or_404(JobApplication, id=application_id, job=job, supplier=supplier)
        
        context = {
            'application': application,
            'job': job,
            'type': 'job'
        }
        return render(request, 'brand_new_site/applicant_detail.html', context)
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def view_internship_applicant_detail(request, internship_id, application_id):
    """View details of a specific internship applicant - ONLY for the employer who posted it"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        
        # Get the internship and verify the supplier owns it
        internship = get_object_or_404(PortalInternship, id=internship_id, supplier=supplier)
        
        # Get the application and verify it belongs to this internship
        application = get_object_or_404(InternshipApplication, id=application_id, internship=internship, supplier=supplier)
        
        context = {
            'application': application,
            'internship': internship,
            'type': 'internship'
        }
        return render(request, 'brand_new_site/applicant_detail.html', context)
    except PermissionDenied:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def preview_application_file(request, application_type, application_id, file_type):
    """Preview a resume or attachment file (PDF/Image) - ONLY for the employer who posted it"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        
        if application_type == 'job':
            application = get_object_or_404(JobApplication, id=application_id, supplier=supplier)
        elif application_type == 'internship':
            application = get_object_or_404(InternshipApplication, id=application_id, supplier=supplier)
        else:
            return Http404("Invalid application type")
        
        # Get the file based on file_type
        if file_type == 'resume':
            file_field = application.resume
            if not file_field:
                return Http404("Resume not found")
        elif file_type == 'attachment':
            file_field = application.additional_attachment
            if not file_field:
                return Http404("Attachment not found")
        else:
            return Http404("Invalid file type")
        
        try:
            # Get the signed URL from Supabase
            signed_url = file_field.url
            logger.info(f"Generated preview URL for {application_type} application {application_id}")
            return JsonResponse({
                'success': True,
                'url': signed_url,
                'filename': file_field.name.split('/')[-1],
                'file_type': file_type
            })
        except Exception as e:
            logger.error(f"Error generating preview URL: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    except PermissionDenied:
        raise PermissionDenied("Access denied.")
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error in preview_application_file: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@supplier_required
def view_resume(request, application_id):
    """Serve the resume inline for a given application (job or internship).
    Sets Content-Disposition to inline so browser opens the file when possible.
    """
    try:
        supplier = get_supplier_for_user_or_raise(request)

        # Try job application first, then internship
        application = None
        try:
            application = JobApplication.objects.get(id=application_id, supplier=supplier)
        except JobApplication.DoesNotExist:
            application = get_object_or_404(InternshipApplication, id=application_id, supplier=supplier)

        if not application.resume:
            raise Http404("Resume not found")

        file_field = application.resume
        filename = file_field.name.split('/')[-1]
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'

        try:
            # Some storage backends provide a file-like object via open()
            fobj = file_field.open('rb')
            response = FileResponse(fobj, content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        except Exception:
            # Fallback to reading into memory
            data = file_field.read()
            bio = BytesIO(data)
            response = FileResponse(bio, content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response

    except PermissionDenied:
        raise PermissionDenied("Access denied.")
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error in view_resume: {str(e)}")
        raise Http404("Error accessing resume")


@supplier_required
def view_attachment(request, application_id):
    """Serve the additional attachment inline for a given application.
    """
    try:
        supplier = get_supplier_for_user_or_raise(request)

        application = None
        try:
            application = JobApplication.objects.get(id=application_id, supplier=supplier)
        except JobApplication.DoesNotExist:
            application = get_object_or_404(InternshipApplication, id=application_id, supplier=supplier)

        if not application.additional_attachment:
            raise Http404("Attachment not found")

        file_field = application.additional_attachment
        filename = file_field.name.split('/')[-1]
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'

        try:
            fobj = file_field.open('rb')
            response = FileResponse(fobj, content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        except Exception:
            data = file_field.read()
            bio = BytesIO(data)
            response = FileResponse(bio, content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response

    except PermissionDenied:
        raise PermissionDenied("Access denied.")
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error in view_attachment: {str(e)}")
        raise Http404("Error accessing attachment")


@supplier_required
def delete_job_applicant(request, job_id, application_id):
    """Delete a job applicant and/or their files - ONLY for the employer who posted it"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        
        # Get the job and verify the supplier owns it
        job = get_object_or_404(PortalJob, id=job_id, supplier=supplier)
        
        # Get the application and verify it belongs to this job
        application = get_object_or_404(JobApplication, id=application_id, job=job, supplier=supplier)
        
        # Check what to delete
        delete_resume_only = request.POST.get('delete_resume_only') == 'true'
        delete_attachment_only = request.POST.get('delete_attachment_only') == 'true'
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            if delete_resume_only:
                # Delete only the resume file
                if application.resume:
                    resume_name = application.resume.name
                    try:
                        # Delete from Supabase storage
                        application.resume.delete()
                        application.resume = None
                        application.save()
                        logger.info(f"Resume deleted for job application {application.id}: {resume_name}")
                        messages.success(request, "Resume deleted successfully.")
                        
                        if is_ajax:
                            return JsonResponse({'success': True, 'message': 'Resume deleted successfully'})
                    except Exception as e:
                        logger.error(f"Error deleting resume from storage: {str(e)}")
                        messages.error(request, f"Error deleting resume: {str(e)}")
                        
                        if is_ajax:
                            return JsonResponse({'success': False, 'error': str(e)}, status=400)
                else:
                    msg = "No resume found to delete."
                    messages.warning(request, msg)
                    
                    if is_ajax:
                        return JsonResponse({'success': False, 'error': msg}, status=400)
            
            elif delete_attachment_only:
                # Delete only the additional attachment
                if application.additional_attachment:
                    attachment_name = application.additional_attachment.name
                    try:
                        # Delete from Supabase storage
                        application.additional_attachment.delete()
                        application.additional_attachment = None
                        application.save()
                        logger.info(f"Attachment deleted for job application {application.id}: {attachment_name}")
                        messages.success(request, "Document deleted successfully.")
                        
                        if is_ajax:
                            return JsonResponse({'success': True, 'message': 'Document deleted successfully'})
                    except Exception as e:
                        logger.error(f"Error deleting attachment from storage: {str(e)}")
                        messages.error(request, f"Error deleting document: {str(e)}")
                        
                        if is_ajax:
                            return JsonResponse({'success': False, 'error': str(e)}, status=400)
                else:
                    msg = "No document found to delete."
                    messages.warning(request, msg)
                    
                    if is_ajax:
                        return JsonResponse({'success': False, 'error': msg}, status=400)
            
            else:
                # Delete entire application and all files
                resume_name = application.resume.name if application.resume else None
                attachment_name = application.additional_attachment.name if application.additional_attachment else None
                
                try:
                    # Delete from Supabase storage
                    if application.resume:
                        application.resume.delete()
                    if application.additional_attachment:
                        application.additional_attachment.delete()
                except Exception as e:
                    logger.error(f"Error deleting files from storage: {str(e)}")
                
                # Delete application record from database
                application.delete()
                logger.info(f"Job application {application_id} deleted completely (resume: {resume_name}, attachment: {attachment_name})")
                messages.success(request, "Application and all associated files deleted successfully.")
                
                if is_ajax:
                    return JsonResponse({'success': True, 'message': 'Application deleted successfully'})
        
        except Exception as e:
            logger.error(f"Error in delete_job_applicant: {str(e)}")
            messages.error(request, f"Error deleting: {str(e)}")
            
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        return redirect('view_job_applicants', job_id=job_id)
    
    except PermissionDenied:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def delete_internship_applicant(request, internship_id, application_id):
    """Delete an internship applicant and/or their files - ONLY for the employer who posted it"""
    try:
        supplier = get_supplier_for_user_or_raise(request)
        
        # Get the internship and verify the supplier owns it
        internship = get_object_or_404(PortalInternship, id=internship_id, supplier=supplier)
        
        # Get the application and verify it belongs to this internship
        application = get_object_or_404(InternshipApplication, id=application_id, internship=internship, supplier=supplier)
        
        # Check what to delete
        delete_resume_only = request.POST.get('delete_resume_only') == 'true'
        delete_attachment_only = request.POST.get('delete_attachment_only') == 'true'
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            if delete_resume_only:
                # Delete only the resume file
                if application.resume:
                    resume_name = application.resume.name
                    try:
                        # Delete from Supabase storage
                        application.resume.delete()
                        application.resume = None
                        application.save()
                        logger.info(f"Resume deleted for internship application {application.id}: {resume_name}")
                        messages.success(request, "Resume deleted successfully.")
                        
                        if is_ajax:
                            return JsonResponse({'success': True, 'message': 'Resume deleted successfully'})
                    except Exception as e:
                        logger.error(f"Error deleting resume from storage: {str(e)}")
                        messages.error(request, f"Error deleting resume: {str(e)}")
                        
                        if is_ajax:
                            return JsonResponse({'success': False, 'error': str(e)}, status=400)
                else:
                    msg = "No resume found to delete."
                    messages.warning(request, msg)
                    
                    if is_ajax:
                        return JsonResponse({'success': False, 'error': msg}, status=400)
            
            elif delete_attachment_only:
                # Delete only the additional attachment
                if application.additional_attachment:
                    attachment_name = application.additional_attachment.name
                    try:
                        # Delete from Supabase storage
                        application.additional_attachment.delete()
                        application.additional_attachment = None
                        application.save()
                        logger.info(f"Attachment deleted for internship application {application.id}: {attachment_name}")
                        messages.success(request, "Document deleted successfully.")
                        
                        if is_ajax:
                            return JsonResponse({'success': True, 'message': 'Document deleted successfully'})
                    except Exception as e:
                        logger.error(f"Error deleting attachment from storage: {str(e)}")
                        messages.error(request, f"Error deleting document: {str(e)}")
                        
                        if is_ajax:
                            return JsonResponse({'success': False, 'error': str(e)}, status=400)
                else:
                    msg = "No document found to delete."
                    messages.warning(request, msg)
                    
                    if is_ajax:
                        return JsonResponse({'success': False, 'error': msg}, status=400)
            
            else:
                # Delete entire application and all files
                resume_name = application.resume.name if application.resume else None
                attachment_name = application.additional_attachment.name if application.additional_attachment else None
                
                try:
                    # Delete from Supabase storage
                    if application.resume:
                        application.resume.delete()
                    if application.additional_attachment:
                        application.additional_attachment.delete()
                except Exception as e:
                    logger.error(f"Error deleting files from storage: {str(e)}")
                
                # Delete application record from database
                application.delete()
                logger.info(f"Internship application {application_id} deleted completely (resume: {resume_name}, attachment: {attachment_name})")
                messages.success(request, "Application and all associated files deleted successfully.")
                
                if is_ajax:
                    return JsonResponse({'success': True, 'message': 'Application deleted successfully'})
        
        except Exception as e:
            logger.error(f"Error in delete_internship_applicant: {str(e)}")
            messages.error(request, f"Error deleting: {str(e)}")
            
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        return redirect('view_internship_applicants', internship_id=internship_id)
    
    except PermissionDenied:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        raise PermissionDenied("Access denied. Only suppliers can access this page.")