from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Announcement
from app.forms import AnnouncementForm

def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement created successfully!')
            return redirect('announcement')
    else:
        form = AnnouncementForm()
    return render(request, 'announcement_create.html', {'form': form})
