import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import (
    Course, Doubt, Enrollment,
    PracticeOnlyQuestion, PracticeSession, PracticeSessionQuestion,
)
from assessments.models import Question, AssessmentAttempt
from .forms import CourseForm
from profiles.models import Certificate
from .streaks import record_engagement


# -----------------------------------------------------------------------------
# Courses
# -----------------------------------------------------------------------------

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

    # Materialize into a list and attach each trainee's own attempt (if any)
    # directly onto the assessment object as .my_attempt, so the template
    # can check `assessment.my_attempt` without needing a variable-keyed
    # dict lookup (Django templates only support literal dict keys).
    assessments = list(assessments)
    if request.user.role == 'TRAINEE' and assessments:
        my_attempts = AssessmentAttempt.objects.filter(
            assessment__in=assessments, trainee=request.user
        )
        attempts_by_id = {a.assessment_id: a for a in my_attempts}
        for a in assessments:
            a.my_attempt = attempts_by_id.get(a.id)
    else:
        for a in assessments:
            a.my_attempt = None

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

    published_assessments = course.assessments.filter(status='PUBLISHED')
    passed_count = 0
    for a in published_assessments:
        passed = AssessmentAttempt.objects.filter(
            assessment=a, trainee=request.user, status='SUBMITTED', score_percent__gte=a.passing_score
        ).exists()
        if passed:
            passed_count += 1

    if published_assessments.exists() and passed_count == published_assessments.count():
        cert_title = f"Completion: {course.title}"
        Certificate.objects.get_or_create(
            user=request.user,
            title=cert_title,
            defaults={
                'issued_by': f"Capacity Connect - {course.trainer.get_full_name()}",
                'issued_date': timezone.now().date(),
            }
        )

        enrollment.is_completed = True
        enrollment.completed_at = timezone.now()
        enrollment.save()

        messages.success(request, f"Congratulations! You have earned your certificate for {course.title}.")
    else:
        messages.error(request, "You must pass all assessments to earn this certificate.")

    return redirect('course_detail', course_id=course.id)


# -----------------------------------------------------------------------------
# Doubts
# -----------------------------------------------------------------------------

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
            record_engagement(request.user)
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
            record_engagement(request.user)  # counts for trainee replies; no-op for trainers
            return redirect('doubt_detail', doubt_id=doubt.id)

    return render(request, 'doubts/doubt_detail.html', {
        'doubt': doubt,
        'comments': doubt.comments.select_related('author'),
        'can_comment': can_comment,
    })


# -----------------------------------------------------------------------------
# Practice
# -----------------------------------------------------------------------------

PRACTICE_QUESTION_COUNT = 10
PRACTICE_TIME_PER_QUESTION = 20  # seconds — used by the frontend countdown


def _build_practice_pool(course):
    """Combines past-assessment questions (published/archived — i.e. no
    longer an active exam) with trainer-authored practice-only questions
    into one uniform list of dicts."""
    pool = []

    past_questions = Question.objects.filter(
        assessment__course=course,
        assessment__status__in=['PUBLISHED', 'ARCHIVED']
    )
    for q in past_questions:
        pool.append({'text': q.question_text, 'options': q.options, 'correct_index': q.correct_index})

    for q in PracticeOnlyQuestion.objects.filter(course=course):
        pool.append({'text': q.question_text, 'options': q.options, 'correct_index': q.correct_index})

    return pool


@login_required
def start_practice(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.role != 'TRAINEE':
        return HttpResponseForbidden("Only trainees can practice.")

    pool = _build_practice_pool(course)
    if not pool:
        messages.info(request, "No practice questions available for this course yet.")
        return redirect('course_detail', course_id=course.id)

    random.shuffle(pool)
    selected = pool[:PRACTICE_QUESTION_COUNT]

    session = PracticeSession.objects.create(course=course, trainee=request.user, total_count=len(selected))
    PracticeSessionQuestion.objects.bulk_create([
        PracticeSessionQuestion(
            session=session, order=i,
            question_text=q['text'], options=q['options'], correct_index=q['correct_index']
        )
        for i, q in enumerate(selected)
    ])

    return redirect('practice_question', session_id=session.id, order=0)


@login_required
def practice_question(request, session_id, order):
    session = get_object_or_404(PracticeSession, id=session_id, trainee=request.user)
    item = get_object_or_404(PracticeSessionQuestion, session=session, order=order)

    if request.method == 'POST' and item.answered_at is None:
        selected = request.POST.get('selected_index', '').strip()
        if selected == '':
            item.timed_out = True
        else:
            item.selected_index = int(selected)
        item.time_taken_seconds = int(request.POST.get('time_taken', 0) or 0)
        item.answered_at = timezone.now()
        item.save()

        if item.is_correct:
            session.correct_count += 1
            session.current_streak += 1
            session.best_streak = max(session.best_streak, session.current_streak)
        else:
            session.current_streak = 0
        session.save()

    is_last = (order + 1) >= session.total_count
    return render(request, 'courses/practice_question.html', {
        'session': session,
        'item': item,
        'order': order,
        'is_last': is_last,
        'time_limit': PRACTICE_TIME_PER_QUESTION,
    })


@login_required
def practice_finish(request, session_id):
    session = get_object_or_404(PracticeSession, id=session_id, trainee=request.user)
    if not session.completed_at:
        session.completed_at = timezone.now()
        session.save()
        record_engagement(request.user)  # practice completion drives the streak now

    return render(request, 'courses/practice_result.html', {'session': session})