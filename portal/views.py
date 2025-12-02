from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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



@login_required
def job_portal_admin(request):
    """Render the job portal admin dashboard"""
    # Filter by user - only show this user's postings
    internships = PortalInternship.objects.filter(posted_by=request.user).order_by('-posted_date')
    jobs = PortalJob.objects.filter(posted_by=request.user).order_by('-posted_date')
    
    # Fetch applications for this user's postings using the job/internship ForeignKey relationships
    # This ensures we only see applications for jobs/internships WE posted
    internship_applications = InternshipApplication.objects.filter(
        internship__posted_by=request.user
    ).order_by('-applied_date')
    
    job_applications = JobApplication.objects.filter(
        job__posted_by=request.user
    ).order_by('-applied_date')

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
        data = json.loads(request.body)
        internship = PortalInternship.objects.create(
            title=data['title'],
            posted_by=request.user,
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
    internships = PortalInternship.objects.filter(posted_by=request.user).order_by('-posted_date')
    
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
        if internship.posted_by != request.user:
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
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def toggle_internship_status(request, internship_id):
    """Toggle internship active status (pause/resume)"""
    try:
        internship = get_object_or_404(PortalInternship, id=internship_id)
        
        # Check ownership
        if internship.posted_by != request.user:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        internship.is_active = not internship.is_active
        internship.save()

        status = 'resumed' if internship.is_active else 'paused'
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def delete_internship(request, internship_id):
    """Delete an internship"""
    try:
        internship = get_object_or_404(PortalInternship, id=internship_id)
        
        # Check ownership
        if internship.posted_by != request.user:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        internship.delete()
        return JsonResponse({
            'success': True,
            'message': 'Internship deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# API Endpoints for Job Management

@csrf_exempt
@csrf_exempt
@require_POST
def add_job(request):
    """Add a new job via AJAX"""
    try:
        data = json.loads(request.body)
        job = PortalJob.objects.create(
            title=data['title'],
            posted_by=request.user,
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
        if job.posted_by != request.user:
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
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def toggle_job_status(request, job_id):
    """Toggle job active status (pause/resume)"""
    try:
        job = get_object_or_404(PortalJob, id=job_id)
        
        # Check ownership
        if job.posted_by != request.user:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        job.is_active = not job.is_active
        job.save()

        status = 'resumed' if job.is_active else 'paused'
        return JsonResponse({
            'success': True,
            'message': f'Job {status} successfully!',
            'is_active': job.is_active
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def delete_job(request, job_id):
    """Delete a job"""
    try:
        job = get_object_or_404(PortalJob, id=job_id)
        
        # Check ownership
        if job.posted_by != request.user:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        job.delete()
        return JsonResponse({
            'success': True,
            'message': 'Job deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# Server-side views for internship management
@login_required
def edit_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    
    # Check if user owns this internship
    if internship.posted_by != request.user:
        raise PermissionDenied("You do not have permission to edit this internship.")

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
    if internship.posted_by != request.user:
        raise PermissionDenied("You do not have permission to delete this internship.")
    
    internship.delete()
    return redirect('job_portal_admin')

@login_required
def toggle_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    
    # Check if user owns this internship
    if internship.posted_by != request.user:
        raise PermissionDenied("You do not have permission to toggle this internship.")
    
    internship.is_active = not internship.is_active
    internship.save()
    return redirect('job_portal_admin')

# Server-side views for job management
@login_required
def edit_job(request, id):
    job = get_object_or_404(PortalJob, id=id)
    
    # Check if user owns this job
    if job.posted_by != request.user:
        raise PermissionDenied("You do not have permission to edit this job.")

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
    if job.posted_by != request.user:
        raise PermissionDenied("You do not have permission to delete this job.")
    
    job.delete()
    return redirect('job_portal_admin')

@login_required
def toggle_job(request, id):
    job = get_object_or_404(PortalJob, id=id)
    
    # Check if user owns this job
    if job.posted_by != request.user:
        raise PermissionDenied("You do not have permission to toggle this job.")
    
    job.is_active = not job.is_active
    job.save()
    return redirect('job_portal_admin')

def internship_application(request, internship_id):
    """Handle internship application form"""
    from .forms import InternshipApplicationForm
    
    # Security check: Only allow applying to active internships
    internship = get_object_or_404(PortalInternship, id=internship_id, is_active=True)

    if request.method == 'POST':
        form = InternshipApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.internship = internship
                application.supplier = internship.supplier
                application.posted_by = internship.posted_by
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
    
    # Security check: Only allow applying to active jobs
    job = get_object_or_404(PortalJob, id=job_id, is_active=True)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.job = job
                application.supplier = job.supplier
                application.posted_by = job.posted_by
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

@login_required
def view_applicants(request, job_id=None, internship_id=None):
    """View applicants for a specific job or internship - ONLY accessible to the employer who posted it"""
    if job_id:
        # Security check: Only the user who posted this job can view applicants
        job = get_object_or_404(PortalJob, id=job_id)
        if job.posted_by != request.user and not request.user.is_superuser:
            raise PermissionDenied("You are not authorized to view applicants for this job.")
        
        applications = JobApplication.objects.filter(job=job).order_by('-applied_date')
        context = {
            'job': job,
            'applications': applications,
            'type': 'job'
        }
        return render(request, 'brand_new_site/view_applicants.html', context)
    
    elif internship_id:
        # Security check: Only the user who posted this internship can view applicants
        internship = get_object_or_404(PortalInternship, id=internship_id)
        if internship.posted_by != request.user and not request.user.is_superuser:
            raise PermissionDenied("You are not authorized to view applicants for this internship.")
        
        applications = InternshipApplication.objects.filter(internship=internship).order_by('-applied_date')
        context = {
            'internship': internship,
            'applications': applications,
            'type': 'internship'
        }
        return render(request, 'brand_new_site/view_applicants.html', context)
    
    else:
        return redirect('job_portal_admin')