from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from .models import PortalInternship, PortalJob, InternshipApplication, JobApplication
from app.models import Supplier

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
        # Show all active internships and jobs from all companies
        internships = PortalInternship.objects.filter(is_active=True)
        jobs = PortalJob.objects.filter(is_active=True)
        vacancies = []

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
                'location': internship.location
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
                'experience': job.experience
            })

        # Collect unique locations from active internships and jobs
        locations = set()
        for internship in internships:
            if internship.location:
                locations.add(internship.location.strip())
        for job in jobs:
            if job.location:
                locations.add(job.location.strip())

        # Sort locations alphabetically
        unique_locations = sorted(list(locations))

        context = {'vacancies': vacancies, 'locations': unique_locations}
    except Exception as e:
        # In a real app, you'd use proper logging
        context = {'vacancies': [], 'locations': [], 'error': str(e)}

    return render(request, 'brand_new_site/dashboard.html', context)


def supplier_required(view_func):
    """Decorator to check if user is a supplier (email exists in Supplier table)"""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            Supplier.objects.get(email=request.user.email)
            return view_func(request, *args, **kwargs)
        except Supplier.DoesNotExist:
            raise PermissionDenied("Access denied. Only suppliers can access this page.")
    return _wrapped_view


@supplier_required
def job_portal_admin(request):
    """Render the job portal admin dashboard"""
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        # Filter by supplier - only show this company's postings
        internships = PortalInternship.objects.filter(supplier=supplier).order_by('-posted_date')
        jobs = PortalJob.objects.filter(supplier=supplier).order_by('-posted_date')
        
        # Fetch applications for this supplier's postings
        internship_applications = InternshipApplication.objects.filter(supplier=supplier).order_by('-applied_date')
        job_applications = JobApplication.objects.filter(supplier=supplier).order_by('-applied_date')
        
        # Add application counts to each internship and job object
        for internship in internships:
            count = InternshipApplication.objects.filter(internship=internship, supplier=supplier).count()
            internship.application_count = count
        
        for job in jobs:
            count = JobApplication.objects.filter(job=job, supplier=supplier).count()
            job.application_count = count
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")

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
        supplier = Supplier.objects.get(email=request.user.email)
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
        return JsonResponse({
            'success': True,
            'id': internship.id,
            'message': 'Internship added successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_GET
def get_internships(request):
    """Get all internships for the admin view"""
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        internships = PortalInternship.objects.filter(supplier=supplier).order_by('-posted_date')
    except Supplier.DoesNotExist:
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
        supplier = Supplier.objects.get(email=request.user.email)
        if internship.supplier != supplier:
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

        return JsonResponse({
            'success': True,
            'message': 'Internship updated successfully!'
        })
    except Supplier.DoesNotExist:
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
        supplier = Supplier.objects.get(email=request.user.email)
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
    except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def delete_internship(request, internship_id):
    """Delete an internship"""
    try:
        internship = get_object_or_404(PortalInternship, id=internship_id)
        
        # Check ownership
        supplier = Supplier.objects.get(email=request.user.email)
        if internship.supplier != supplier:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        internship.delete()
        return JsonResponse({
            'success': True,
            'message': 'Internship deleted successfully!'
        })
    except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# API Endpoints for Job Management

@csrf_exempt
@csrf_exempt
@require_POST
def add_job(request):
    """Add a new job via AJAX"""
    try:
        supplier = Supplier.objects.get(email=request.user.email)
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
def update_job(request, job_id):
    """Update an existing job"""
    try:
        job = get_object_or_404(PortalJob, id=job_id)
        
        # Check ownership
        supplier = Supplier.objects.get(email=request.user.email)
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
    except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def toggle_job_status(request, job_id):
    """Toggle job active status (pause/resume)"""
    try:
        job = get_object_or_404(PortalJob, id=job_id)
        
        # Check ownership
        supplier = Supplier.objects.get(email=request.user.email)
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
    except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def delete_job(request, job_id):
    """Delete a job"""
    try:
        job = get_object_or_404(PortalJob, id=job_id)
        
        # Check ownership
        supplier = Supplier.objects.get(email=request.user.email)
        if job.supplier != supplier:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        job.delete()
        return JsonResponse({
            'success': True,
            'message': 'Job deleted successfully!'
        })
    except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# Server-side views for internship management
@login_required
def edit_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    
    # Check if user owns this internship
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        if internship.supplier != supplier:
            raise PermissionDenied("You do not have permission to edit this internship.")
    except Supplier.DoesNotExist:
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
        supplier = Supplier.objects.get(email=request.user.email)
        if internship.supplier != supplier:
            raise PermissionDenied("You do not have permission to delete this internship.")
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can delete internships.")
    
    internship.delete()
    return redirect('job_portal_admin')

@login_required
def toggle_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    
    # Check if user owns this internship
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        if internship.supplier != supplier:
            raise PermissionDenied("You do not have permission to toggle this internship.")
    except Supplier.DoesNotExist:
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
        supplier = Supplier.objects.get(email=request.user.email)
        if job.supplier != supplier:
            raise PermissionDenied("You do not have permission to edit this job.")
    except Supplier.DoesNotExist:
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
def delete_job_view(request, id):
    job = get_object_or_404(PortalJob, id=id)
    
    # Check if user owns this job
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        if job.supplier != supplier:
            raise PermissionDenied("You do not have permission to delete this job.")
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can delete jobs.")
    
    job.delete()
    return redirect('job_portal_admin')

@login_required
def toggle_job(request, id):
    job = get_object_or_404(PortalJob, id=id)
    
    # Check if user owns this job
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        if job.supplier != supplier:
            raise PermissionDenied("You do not have permission to toggle this job.")
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can toggle jobs.")
    
    job.is_active = not job.is_active
    job.save()
    return redirect('job_portal_admin')

def internship_application(request, internship_id):
    """Handle internship application form"""
    from .forms import InternshipApplicationForm
    
    internship = get_object_or_404(PortalInternship, id=internship_id, is_active=True)

    if request.method == 'POST':
        form = InternshipApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.internship = internship
                application.supplier = internship.supplier
                application.save()
                messages.success(request, 'Your internship application has been submitted successfully!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error submitting application: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = InternshipApplicationForm()

    context = {
        'internship': internship,
        'form': form
    }
    return render(request, 'brand_new_site/internship_application.html', context)

def job_application(request, job_id):
    """Handle job application form"""
    from .forms import JobApplicationForm
    import json
    
    job = get_object_or_404(PortalJob, id=job_id, is_active=True)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.job = job
                application.supplier = job.supplier
                application.save()
                messages.success(request, 'Your job application has been submitted successfully!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error submitting application: {str(e)}')
        else:
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
        supplier = Supplier.objects.get(email=request.user.email)
        
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
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def view_internship_applicants(request, internship_id):
    """View all applicants for a specific internship - ONLY for the employer who posted it"""
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        
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
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def view_job_applicant_detail(request, job_id, application_id):
    """View details of a specific job applicant - ONLY for the employer who posted it"""
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        
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
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def view_internship_applicant_detail(request, internship_id, application_id):
    """View details of a specific internship applicant - ONLY for the employer who posted it"""
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        
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
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def delete_job_applicant(request, job_id, application_id):
    """Delete a job applicant and/or their resume - ONLY for the employer who posted it"""
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        
        # Get the job and verify the supplier owns it
        job = get_object_or_404(PortalJob, id=job_id, supplier=supplier)
        
        # Get the application and verify it belongs to this job
        application = get_object_or_404(JobApplication, id=application_id, job=job, supplier=supplier)
        
        # Check if only deleting resume
        delete_resume_only = request.POST.get('delete_resume_only') == 'true'
        
        if delete_resume_only:
            # Delete the resume file if it exists
            if application.resume:
                application.resume.delete()
                application.resume = None
                application.save()
        else:
            # Delete entire application
            if application.resume:
                application.resume.delete()
            if application.additional_attachment:
                application.additional_attachment.delete()
            application.delete()
        
        return redirect('view_job_applicants', job_id=job_id)
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")


@supplier_required
def delete_internship_applicant(request, internship_id, application_id):
    """Delete an internship applicant and/or their resume - ONLY for the employer who posted it"""
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        
        # Get the internship and verify the supplier owns it
        internship = get_object_or_404(PortalInternship, id=internship_id, supplier=supplier)
        
        # Get the application and verify it belongs to this internship
        application = get_object_or_404(InternshipApplication, id=application_id, internship=internship, supplier=supplier)
        
        # Check if only deleting resume
        delete_resume_only = request.POST.get('delete_resume_only') == 'true'
        
        if delete_resume_only:
            # Delete the resume file if it exists
            if application.resume:
                application.resume.delete()
                application.resume = None
                application.save()
        else:
            # Delete entire application
            if application.resume:
                application.resume.delete()
            if application.additional_attachment:
                application.additional_attachment.delete()
            application.delete()
        
        return redirect('view_internship_applicants', internship_id=internship_id)
    except Supplier.DoesNotExist:
        raise PermissionDenied("Access denied. Only suppliers can access this page.")