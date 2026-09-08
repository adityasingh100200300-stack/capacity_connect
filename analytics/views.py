from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Count, Avg, F, Q

from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assessments.models import AssessmentAttempt
from profiles.models import Certificate

@login_required
def admin_dashboard(request):
    """
    Overview dashboard for Admins summarizing platform statistics.
    """
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Access restricted to Administrators.")

    # User Metrics
    total_trainees = CustomUser.objects.filter(role='TRAINEE', status='ACTIVE').count()
    total_trainers = CustomUser.objects.filter(role='TRAINER', status='ACTIVE').count()
    pending_users = CustomUser.objects.filter(status='PENDING').count()

    # Course Metrics
    total_courses = Course.objects.filter(is_active=True).count()
    total_enrollments = Enrollment.objects.count()

    # Assessment Metrics
    total_attempts = AssessmentAttempt.objects.count()
    passed_attempts = AssessmentAttempt.objects.filter(
        status='SUBMITTED', 
        score_percent__gte=F('assessment__passing_score')
    ).count()

    # Certification Metrics
    total_certificates = Certificate.objects.count()

    context = {
        'total_trainees': total_trainees,
        'total_trainers': total_trainers,
        'pending_users': pending_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'total_certificates': total_certificates,
    }

    return render(request, 'analytics/dashboard.html', context)
