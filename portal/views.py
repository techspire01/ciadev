from django.shortcuts import render

# Create your views here.

def dashboard(request):
    """Main dashboard with new red/pink theme"""
    vacancies = [
        {
            'role': 'Software Engineer',
            'company_name': 'Tech Corp',
            'package': '₹12 LPA',
            'job_description': 'Develop and maintain software solutions.',
            'type': 'job'
        },
        {
            'role': 'Marketing Intern',
            'company_name': 'Marketify',
            'package': '₹20K/month',
            'job_description': 'Assist marketing team with campaigns.',
            'type': 'internship'
        },
        {
            'role': 'Data Analyst',
            'company_name': 'Data Insights',
            'package': '₹8 LPA',
            'job_description': 'Analyze data to provide actionable insights.',
            'type': 'job'
        },
    ]
    context = {'vacancies': vacancies}
    return render(request, 'brand_new_site/dashboard.html', context)

def details(request):
    """Opportunity details page"""
    return render(request, 'brand_new_site/details.html')

def internship_job(request):
    vacancies = [
        {
            'role': 'Software Engineer',
            'company_name': 'Tech Corp',
            'package': '₹12 LPA',
            'job_description': 'Develop and maintain software solutions.',
            'type': 'job'
        },
        {
            'role': 'Marketing Intern',
            'company_name': 'Marketify',
            'package': '₹20K/month',
            'job_description': 'Assist marketing team with campaigns.',
            'type': 'internship'
        },
        {
            'role': 'Data Analyst',
            'company_name': 'Data Insights',
            'package': '₹8 LPA',
            'job_description': 'Analyze data to provide actionable insights.',
            'type': 'job'
        },
    ]
    context = {'vacancies': vacancies}
    return render(request, 'brand_new_site/dashboard.html', context)

def intern_apply_form(request):
    return render(request, 'portal/intern_apply_form.html')

def job_apply_form(request):
    return render(request, 'portal/job_apply_form.html')

def brand_new_site_dashboard(request):
    """Render the brand new site dashboard"""
    vacancies = [
        {
            'role': 'Software Engineer',
            'company_name': 'Tech Corp',
            'package': '₹12 LPA',
            'job_description': 'Develop and maintain software solutions.',
            'type': 'job'
        },
        {
            'role': 'Marketing Intern',
            'company_name': 'Marketify',
            'package': '₹20K/month',
            'job_description': 'Assist marketing team with campaigns.',
            'type': 'internship'
        },
        {
            'role': 'Data Analyst',
            'company_name': 'Data Insights',
            'package': '₹8 LPA',
            'job_description': 'Analyze data to provide actionable insights.',
            'type': 'job'
        },
    ]
    context = {'vacancies': vacancies}
    return render(request, 'brand_new_site/dashboard.html', context)

def job_portal_admin(request):
    """Render the job portal admin dashboard"""
    return render(request, 'brand_new_site/job_portal_admin.html')

def job_admin(request):
    """Render the job admin UI model page"""
    return render(request, 'brand_new_site/job_admin.html')
