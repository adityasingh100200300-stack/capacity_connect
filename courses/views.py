from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from django.utils import timezone
from .models import Course, Enrollment
from .forms import CourseForm
from assessments.models import AssessmentAttempt
from profiles.models import Certificate

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
 
from .models import Course, Doubt

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
    
    if request.user == course.trainer:
        assessments = course.assessments.all()
    else:
        assessments = course.assessments.filter(status='PUBLISHED') if is_enrolled else []
    feedbacks = course.feedbacks.select_related('user').order_by('-created_at')[:5]

    # Check if trainee has earned a certificate
    has_certificate = False
    can_generate_certificate = False
    
    if request.user.role == 'TRAINEE' and is_enrolled:
        has_certificate = Certificate.objects.filter(user=request.user, title=f"Completion: {course.title}").exists()
        
        if not has_certificate:
            published_assessments = course.assessments.filter(status='PUBLISHED')
            if published_assessments.exists():
                passed_count = 0
                for a in published_assessments:
                    passed_attempt = AssessmentAttempt.objects.filter(
                        assessment=a, 
                        trainee=request.user, 
                        status='SUBMITTED',
                        score_percent__gte=a.passing_score
                    ).exists()
                    if passed_attempt:
                        passed_count += 1
                
                if passed_count == published_assessments.count():
                    can_generate_certificate = True

    return render(request, 'courses/detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'resources': resources,
        'assessments': assessments,
        'feedbacks': feedbacks,
        'has_certificate': has_certificate,
        'can_generate_certificate': can_generate_certificate,
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


@login_required
def generate_certificate_view(request, course_id):
    """Generates a certificate for the trainee if they passed all assessments."""
    if request.user.role != 'TRAINEE':
        return redirect('course_detail', course_id=course_id)
        
    course = get_object_or_404(Course, id=course_id, is_active=True)
    enrollment = get_object_or_404(Enrollment, course=course, trainee=request.user)
    
    # Validate they passed everything
    published_assessments = course.assessments.filter(status='PUBLISHED')
    passed_count = 0
    for a in published_assessments:
        passed = AssessmentAttempt.objects.filter(
            assessment=a, trainee=request.user, status='SUBMITTED', score_percent__gte=a.passing_score
        ).exists()
        if passed:
            passed_count += 1
            
    if published_assessments.exists() and passed_count == published_assessments.count():
        # Generate Certificate
        cert_title = f"Completion: {course.title}"
        Certificate.objects.get_or_create(
            user=request.user,
            title=cert_title,
            defaults={
                'issued_by': f"Capacity Connect - {course.trainer.get_full_name()}",
                'issued_date': timezone.now().date(),
            }
        )
        
        # Mark enrollment complete
        enrollment.is_completed = True
        enrollment.completed_at = timezone.now()
        enrollment.save()
        
        messages.success(request, f"Congratulations! You have earned your certificate for {course.title}.")
    else:
        messages.error(request, "You must pass all assessments to earn this certificate.")
        
    return redirect('course_detail', course_id=course.id)

def _can_comment(user, doubt):
    """Only the trainee who raised the doubt, or the course's trainer, may reply."""
    if user.id == doubt.trainee_id:
        return True
    if user.role == 'TRAINER' and user.id == doubt.course.trainer_id:
        return True
    return False
 
 
@login_required
def doubt_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    doubts = course.doubts.select_related('trainee')
    return render(request, 'doubts/doubt_list.html', {'course': course, 'doubts': doubts})
 
 
@login_required
def create_doubt(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.role != 'TRAINEE':
        return HttpResponseForbidden("Only trainees can raise a doubt.")
 
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        if title and body:
            Doubt.objects.create(course=course, trainee=request.user, title=title, body=body)
            messages.success(request, "Your doubt has been posted.")
            return redirect('doubt_list', course_id=course.id)
        messages.error(request, "Fill in both a title and a description.")
 
    return render(request, 'doubts/create_doubt.html', {'course': course})
 
 
@login_required
def doubt_detail(request, doubt_id):
    doubt = get_object_or_404(Doubt, id=doubt_id)
    can_comment = _can_comment(request.user, doubt)
 
    if request.method == 'POST':
        if not can_comment:
            return HttpResponseForbidden("You can't comment on this doubt.")
        body = request.POST.get('body', '').strip()
        if body:
            doubt.comments.create(author=request.user, body=body)
            return redirect('doubt_detail', doubt_id=doubt.id)
 
    return render(request, 'doubts/doubt_detail.html', {
        'doubt': doubt,
        'comments': doubt.comments.select_related('author'),
        'can_comment': can_comment,
    })
