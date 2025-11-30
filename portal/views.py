from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from .models import PortalInternship, PortalJob

# Create your views here.

def dashboard(request):
    """Main dashboard with new red/pink theme"""
    internships = PortalInternship.objects.filter(is_active=True)
    jobs = PortalJob.objects.filter(is_active=True)
    vacancies = []

    for internship in internships:
        vacancies.append({
            'role': internship.title,
            'company_name': internship.company_name,
            'package': internship.salary,
            'job_description': internship.description,
            'type': 'internship'
        })

    for job in jobs:
        vacancies.append({
            'role': job.title,
            'company_name': job.company_name,
            'package': job.salary,
            'job_description': job.description,
            'type': 'job'
        })

    context = {'vacancies': vacancies}
    return render(request, 'brand_new_site/dashboard.html', context)

def details(request):
    """Opportunity details page"""
    return render(request, 'brand_new_site/details.html')

def internship_job(request):
    internships = PortalInternship.objects.filter(is_active=True)
    jobs = PortalJob.objects.filter(is_active=True)
    vacancies = []

    for internship in internships:
        vacancies.append({
            'role': internship.title,
            'company_name': internship.company_name,
            'package': internship.salary,
            'job_description': internship.description,
            'type': 'internship'
        })

    for job in jobs:
        vacancies.append({
            'role': job.title,
            'company_name': job.company_name,
            'package': job.salary,
            'job_description': job.description,
            'type': 'job'
        })

    context = {'vacancies': vacancies}
    return render(request, 'brand_new_site/dashboard.html', context)

def intern_apply_form(request):
    return render(request, 'portal/intern_apply_form.html')

def job_apply_form(request):
    return render(request, 'portal/job_apply_form.html')

def brand_new_site_dashboard(request):
    """Render the brand new site dashboard"""
    internships = PortalInternship.objects.filter(is_active=True)
    jobs = PortalJob.objects.filter(is_active=True)
    vacancies = []

    for internship in internships:
        vacancies.append({
            'role': internship.title,
            'company_name': internship.company_name,
            'package': internship.salary,
            'job_description': internship.description,
            'type': 'internship'
        })

    for job in jobs:
        vacancies.append({
            'role': job.title,
            'company_name': job.company_name,
            'package': job.salary,
            'job_description': job.description,
            'type': 'job'
        })

    context = {'vacancies': vacancies}
    return render(request, 'brand_new_site/dashboard.html', context)

def job_portal_admin(request):
    """Render the job portal admin dashboard"""
    internships = PortalInternship.objects.all().order_by('-posted_date')
    jobs = PortalJob.objects.all().order_by('-posted_date')

    return render(request, 'brand_new_site/job_portal_admin.html', {
        'internships': internships,
        'jobs': jobs
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
            title=data['role'],
            company_name=data['company'],
            duration=data.get('duration', ''),
            salary=data.get('stipend', ''),
            description=data.get('description', ''),
            email=data.get('email', ''),
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
    internships = PortalInternship.objects.all().order_by('-posted_date')
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
        data = json.loads(request.body)

        internship.title = data.get('role', internship.title)
        internship.company_name = data.get('company', internship.company_name)
        internship.duration = data.get('duration', internship.duration)
        internship.salary = data.get('stipend', internship.salary)
        internship.description = data.get('description', internship.description)
        internship.email = data.get('email', internship.email)
        internship.requirements = data.get('requirements', internship.requirements)
        internship.responsibilities = data.get('responsibilities', internship.responsibilities)
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
        internship.is_active = not internship.is_active
        internship.save()

        status = 'resumed' if internship.is_active else 'paused'
        return JsonResponse({
            'success': True,
            'message': f'Internship {status} successfully!',
            'is_active': internship.is_active
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def delete_internship(request, internship_id):
    """Delete an internship"""
    try:
        internship = get_object_or_404(PortalInternship, id=internship_id)
        internship.delete()
        return JsonResponse({
            'success': True,
            'message': 'Internship deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# API Endpoints for Job Management

@csrf_exempt
@require_POST
def add_job(request):
    """Add a new job via AJAX"""
    try:
        data = json.loads(request.body)
        job = PortalJob.objects.create(
            title=data['title'],
            company_name=data['company'],
            location=data.get('location', ''),
            salary=data.get('salary', ''),
            description=data.get('description', ''),
            email=data.get('email', ''),
            requirements=data.get('requirements', ''),
            responsibilities=data.get('responsibilities', '')
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
        data = json.loads(request.body)

        job.title = data.get('title', job.title)
        job.company_name = data.get('company', job.company_name)
        job.location = data.get('location', job.location)
        job.salary = data.get('salary', job.salary)
        job.description = data.get('description', job.description)
        job.email = data.get('email', job.email)
        job.requirements = data.get('requirements', job.requirements)
        job.responsibilities = data.get('responsibilities', job.responsibilities)
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
        job.delete()
        return JsonResponse({
            'success': True,
            'message': 'Job deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# Server-side views for internship management
def edit_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)

    if request.method == 'POST':
        internship.title = request.POST.get('role')
        internship.company_name = request.POST.get('company')
        internship.duration = request.POST.get('duration')
        internship.salary = request.POST.get('stipend')
        internship.email = request.POST.get('email')
        internship.description = request.POST.get('description')
        internship.requirements = request.POST.get('requirements')
        internship.responsibilities = request.POST.get('responsibilities')
        internship.save()
        return redirect('job_portal_admin')

    return redirect('job_portal_admin')

def delete_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    internship.delete()
    return redirect('job_portal_admin')

def toggle_internship(request, id):
    internship = get_object_or_404(PortalInternship, id=id)
    internship.is_active = not internship.is_active
    internship.save()
    return redirect('job_portal_admin')

# Server-side views for job management
def edit_job(request, id):
    job = get_object_or_404(PortalJob, id=id)

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.company_name = request.POST.get('company')
        job.location = request.POST.get('location')
        job.salary = request.POST.get('salary')
        job.email = request.POST.get('email')
        job.description = request.POST.get('description')
        job.requirements = request.POST.get('requirements')
        job.responsibilities = request.POST.get('responsibilities')
        job.save()
        return redirect('job_portal_admin')

    return redirect('job_portal_admin')

def delete_job(request, id):
    job = get_object_or_404(PortalJob, id=id)
    job.delete()
    return redirect('job_portal_admin')

def toggle_job(request, id):
    job = get_object_or_404(PortalJob, id=id)
    job.is_active = not job.is_active
    job.save()
    return redirect('job_portal_admin')
