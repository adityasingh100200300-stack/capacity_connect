from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Announcement
from .forms import AnnouncementForm


def home_view(request):
    """Public landing page — shown at the site root. Includes latest announcement banner."""
    latest_announcement = Announcement.objects.order_by('-is_pinned', '-created_at').first()
    all_announcements = Announcement.objects.select_related('created_by').all()[:6]
    return render(request, 'home.html', {
        'latest_announcement': latest_announcement,
        'all_announcements': all_announcements,
    })


def announcement_list_view(request):
    """Full announcements feed page."""
    announcements = Announcement.objects.select_related('created_by').all()[:15]
    latest_announcement = announcements.first() if announcements else None
    return render(request, 'announcements/list.html', {
        'announcements': announcements,
        'latest_announcement': latest_announcement,
    })


@login_required
def create_announcement_view(request):
    """Admin-only: publish a new announcement."""
    if request.user.role != 'ADMIN':
        messages.error(request, 'Only admins can publish announcements.')
        return redirect('announcement_list')

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, f'Announcement "{announcement.title}" published.')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()

    return render(request, 'announcements/create.html', {'form': form})
