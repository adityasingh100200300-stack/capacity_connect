from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import Course, Enrollment
from .forms import CourseForm


@login_required
def course_list_view(request):
    """
    All active courses.
    Trainees see an Enroll button; trainers and admins see all courses.
    """
    courses = Course.objects.filter(is_active=True).select_related('trainer').annotate(
        enrollment_count=Count('enrollments')
    )

    enrolled_ids = set()
    if request.user.role == 'TRAINEE':
        enrolled_ids = set(
            Enrollment.objects.filter(trainee=request.user).values_list('course_id', flat=True)
        )

    return render(request, 'courses/list.html', {
        'courses': courses,
        'enrolled_ids': enrolled_ids,
    })


@login_required
def course_detail_view(request, course_id):
    """
    Course detail page.
    - Trainees must be enrolled to see library resources and assessments.
    - Trainers and Admins always see everything.
    """
    course = get_object_or_404(Course, id=course_id, is_active=True)
    is_enrolled = False
    enrollment = None

    if request.user.role == 'TRAINEE':
        enrollment = Enrollment.objects.filter(trainee=request.user, course=course).first()
        is_enrolled = enrollment is not None
    elif request.user.role in ('TRAINER', 'ADMIN'):
        is_enrolled = True  # Trainers/admins see all content

    resources = course.resources.all() if is_enrolled else []
    assessments = course.assessments.filter(status='PUBLISHED') if is_enrolled else []
    feedbacks = course.feedbacks.select_related('user').order_by('-created_at')[:5]

    return render(request, 'courses/detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'resources': resources,
        'assessments': assessments,
        'feedbacks': feedbacks,
    })


@login_required
def enroll_view(request, course_id):
    """POST-only: enroll the current trainee in a course."""
    if request.user.role != 'TRAINEE':
        messages.error(request, 'Only trainees can enroll in courses.')
        return redirect('course_list')

    course = get_object_or_404(Course, id=course_id, is_active=True)
    _, created = Enrollment.objects.get_or_create(trainee=request.user, course=course)

    if created:
        messages.success(request, f'You are now enrolled in "{course.title}".')
    else:
        messages.info(request, f'You are already enrolled in "{course.title}".')

    return redirect('course_detail', course_id=course.id)


@login_required
def create_course_view(request):
    """Trainer-only: create a new course."""
    if request.user.role not in ('TRAINER', 'ADMIN'):
        messages.error(request, 'Only trainers can create courses.')
        return redirect('course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.trainer = request.user
            course.save()
            messages.success(request, f'Course "{course.title}" created.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm()

    return render(request, 'courses/create.html', {'form': form})


@login_required
def trainer_dashboard_view(request):
    """Trainer's view of their own courses with enrollment stats."""
    if request.user.role not in ('TRAINER', 'ADMIN'):
        return redirect('course_list')

    if request.user.role == 'ADMIN':
        # Admins see all courses across all trainers
        courses = Course.objects.all().select_related('trainer').annotate(
            enrollment_count=Count('enrollments')
        )
    else:
        courses = Course.objects.filter(trainer=request.user).annotate(
            enrollment_count=Count('enrollments')
        )

    return render(request, 'courses/trainer_dashboard.html', {'courses': courses})
