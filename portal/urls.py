from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('internship_job/', views.internship_job, name='internship_job'),
    path('intern_apply_form/', views.intern_apply_form, name='intern_apply_form'),
    path('job_apply_form/', views.job_apply_form, name='job_apply_form'),
]
