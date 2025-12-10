from django.contrib import admin
from django import forms
from .models import PortalInternship, PortalJob


@admin.register(PortalInternship)
class PortalInternshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'salary', 'is_active', 'posted_date')
    list_filter = ('is_active', 'posted_date')
    search_fields = ('title', 'company_name', 'email')
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'description', 'supplier', 'company_name', 'email', 'is_active')}),
        ('Details', {'fields': ('duration', 'salary', 'location', 'requirements', 'responsibilities')}),
        ('Image', {'fields': ('image', 'image_url')}),
        ('Timestamps', {'fields': ('posted_date',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('posted_date',)


@admin.register(PortalJob)
class PortalJobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'salary', 'is_active', 'posted_date')
    list_filter = ('is_active', 'posted_date')
    search_fields = ('title', 'company_name', 'email')
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'description', 'supplier', 'company_name', 'email', 'is_active')}),
        ('Details', {'fields': ('location', 'salary', 'experience', 'requirements', 'responsibilities')}),
        ('Image', {'fields': ('image', 'image_url')}),
        ('Timestamps', {'fields': ('posted_date',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('posted_date',)