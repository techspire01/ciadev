from django.shortcuts import render

# Create your views here.

def dashboard(request):
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
    return render(request, 'dashboard.html', context)

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
    return render(request, 'dashboard.html', context)

def intern_apply_form(request):
    return render(request, 'intern_apply_form.html')

def job_apply_form(request):
    return render(request, 'job_apply_form.html')
