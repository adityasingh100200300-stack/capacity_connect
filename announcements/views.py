from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Announcement
from .forms import AnnouncementForm


def home_view(request):
    """Public landing page — shown at the site root. When authenticated, renders personalized role-based LMS dashboard."""
    latest_announcement = Announcement.objects.order_by('-is_pinned', '-created_at').first()
    all_announcements = Announcement.objects.select_related('created_by').all()[:6]

    context = {
        'latest_announcement': latest_announcement,
        'all_announcements': all_announcements,
    }

    if request.user.is_authenticated:
        from courses.models import Course, Enrollment, Doubt
        from assessments.models import AssessmentAttempt
        from accounts.models import CustomUser

        role = getattr(request.user, 'role', 'TRAINEE')

        if role == 'TRAINEE':
            enrolled_qs = Enrollment.objects.filter(trainee=request.user).select_related('course', 'course__trainer')
            enrolled_count = enrolled_qs.count()
            completed_count = enrolled_qs.filter(is_completed=True).count()
            assessments_count = AssessmentAttempt.objects.filter(trainee=request.user, status='SUBMITTED').count()
            avg_progress = int((completed_count / enrolled_count) * 100) if enrolled_count > 0 else 0

            context.update({
                'enrolled_enrollments': enrolled_qs,
                'trainee_stats': {
                    'enrolled': enrolled_count,
                    'completed': completed_count,
                    'assessments': assessments_count,
                    'avg_progress': avg_progress,
                }
            })

        elif role == 'TRAINER':
            trainer_courses = Course.objects.filter(trainer=request.user)
            total_courses = trainer_courses.count()
            total_enrollees = Enrollment.objects.filter(course__in=trainer_courses).count()
            completed_count = Enrollment.objects.filter(course__in=trainer_courses, is_completed=True).count()
            pending_doubts = Doubt.objects.filter(course__in=trainer_courses, is_resolved=False).count()

            context.update({
                'trainer_courses': trainer_courses[:6],
                'trainer_stats': {
                    'total_courses': total_courses,
                    'total_enrollees': total_enrollees,
                    'completed_count': completed_count,
                    'pending_doubts': pending_doubts,
                }
            })

        elif role == 'ADMIN':
            total_users = CustomUser.objects.count()
            total_courses = Course.objects.count()
            total_trainees = CustomUser.objects.filter(role='TRAINEE').count()
            completions = Enrollment.objects.filter(is_completed=True).count()
            pending_users = CustomUser.objects.filter(status='PENDING').order_by('-date_joined')[:5]
            pending_count = CustomUser.objects.filter(status='PENDING').count()

            context.update({
                'admin_stats': {
                    'total_users': total_users,
                    'total_courses': total_courses,
                    'total_trainees': total_trainees,
                    'completions': completions,
                },
                'pending_users': pending_users,
                'pending_count': pending_count,
            })

    return render(request, 'home.html', context)


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
