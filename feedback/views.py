from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from courses.models import Course, Enrollment
from .models import CourseFeedback
from .forms import FeedbackForm


@login_required
def submit_feedback_view(request, course_id):
    """Trainee submits feedback for a course they are enrolled in."""
    course = get_object_or_404(Course, id=course_id)

    # Only enrolled trainees can submit feedback
    if request.user.role == 'TRAINEE':
        if not Enrollment.objects.filter(trainee=request.user, course=course).exists():
            messages.error(request, 'You must be enrolled in this course to leave feedback.')
            return redirect('course_detail', course_id=course.id)

    # Check for existing feedback
    existing = CourseFeedback.objects.filter(user=request.user, course=course).first()
    if existing:
        messages.info(request, 'You have already submitted feedback for this course.')
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.course = course
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = FeedbackForm()

    return render(request, 'feedback/submit.html', {'form': form, 'course': course})


@login_required
def course_feedback_list_view(request, course_id):
    """Trainer or Admin: see all feedback for a specific course."""
    if request.user.role not in ('TRAINER', 'ADMIN'):
        messages.error(request, 'Only trainers and admins can view feedback summaries.')
        return redirect('course_list')

    course = get_object_or_404(Course, id=course_id)
    feedbacks = CourseFeedback.objects.filter(course=course).select_related('user')

    # Simple stats
    avg_rating = None
    if feedbacks.exists():
        avg_rating = round(sum(f.rating for f in feedbacks) / feedbacks.count(), 1)

    return render(request, 'feedback/list.html', {
        'course': course,
        'feedbacks': feedbacks,
        'avg_rating': avg_rating,
    })
