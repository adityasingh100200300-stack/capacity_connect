from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Assessment, AssessmentAttempt, AttemptAnswer, Question
from .services import submit_and_grade_attempt
from .forms import AssessmentForm, QuestionForm
from courses.models import Course

@login_required
def start_assessment(request, assessment_id):
    """Creates the timestamped attempt and redirects to the exam room."""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Get existing attempt or create a new one (started_at is set automatically)
    attempt, created = AssessmentAttempt.objects.get_or_create(
        assessment=assessment,
        trainee=request.user,
        defaults={'status': 'IN_PROGRESS'}
    )
    
    # If they already finished this exam, send them to the results
    if attempt.status != 'IN_PROGRESS':
        return redirect('assessment_result', attempt_id=attempt.id)
        
    return redirect('take_assessment', attempt_id=attempt.id)

@login_required
def take_assessment(request, attempt_id):
    """Renders the exam and enforces the strict time limit upon submission."""
    attempt = get_object_or_404(AssessmentAttempt, id=attempt_id, trainee=request.user)
    
    if attempt.status != 'IN_PROGRESS':
        return redirect('assessment_result', attempt_id=attempt.id)
        
    # Calculate exactly how much time has passed on the server
    elapsed_seconds = (timezone.now() - attempt.started_at).total_seconds()
    allowed_seconds = attempt.assessment.duration_minutes * 60
    
    # Check if the user is submitting the form OR if their time ran out
    if request.method == 'POST' or elapsed_seconds > (allowed_seconds + 30): # 30s grace period for network latency
        
        # Only save answers if they actually submitted the form within the time limit
        if request.method == 'POST' and elapsed_seconds <= (allowed_seconds + 30):
            for question in attempt.assessment.questions.all():
                selected = request.POST.get(f'question_{question.id}')
                if selected is not None:
                    AttemptAnswer.objects.update_or_create(
                        attempt=attempt,
                        question=question,
                        defaults={'selected_index': int(selected)}
                    )
        elif elapsed_seconds > (allowed_seconds + 30):
            attempt.status = 'EXPIRED'
            attempt.save()
            
        # Trigger the grading engine service you wrote earlier
        submit_and_grade_attempt(attempt.id)
        return redirect('assessment_result', attempt_id=attempt.id)
        
    return render(request, 'assessments/take.html', {'attempt': attempt, 'allowed_seconds': allowed_seconds})

@login_required
def assessment_result(request, attempt_id):
    """Displays the final score to the trainee."""
    attempt = get_object_or_404(AssessmentAttempt, id=attempt_id, trainee=request.user)
    return render(request, 'assessments/result.html', {'attempt': attempt})


# -----------------------------------------------------------------------------
# Trainer Management Views
# -----------------------------------------------------------------------------

@login_required
def create_assessment(request, course_id):
    """Allows a trainer to create a new assessment for their course."""
    course = get_object_or_404(Course, id=course_id)
    
    if course.trainer != request.user:
        return HttpResponseForbidden("You are not the trainer for this course.")
        
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.course = course
            assessment.status = 'DRAFT'
            assessment.save()
            messages.success(request, "Assessment created. You can now add questions.")
            return redirect('manage_assessment', assessment_id=assessment.id)
    else:
        form = AssessmentForm()
        
    return render(request, 'assessments/create.html', {'form': form, 'course': course})


@login_required
def manage_assessment(request, assessment_id):
    """Dashboard for a trainer to view/add questions and publish the assessment."""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    if assessment.course.trainer != request.user:
        return HttpResponseForbidden("You are not the trainer for this course.")
        
    questions = assessment.questions.all()
    form = QuestionForm()
    
    return render(request, 'assessments/manage.html', {
        'assessment': assessment,
        'questions': questions,
        'form': form,
    })


@login_required
def add_question(request, assessment_id):
    """Handles POST request to add a question to an assessment."""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    if assessment.course.trainer != request.user:
        return HttpResponseForbidden("You are not the trainer for this course.")
        
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assessment = assessment
            # options_text is already cleaned and converted to a list by the form
            question.options = form.cleaned_data['options_text']
            question.save()
            messages.success(request, "Question added successfully.")
        else:
            messages.error(request, "Error adding question. Please check your inputs.")
            # In a full robust app, we might re-render the page with errors.
            # For simplicity, we just redirect back to manage.
            
    return redirect('manage_assessment', assessment_id=assessment.id)


@login_required
def publish_assessment(request, assessment_id):
    """Changes the assessment status from DRAFT to PUBLISHED."""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    if assessment.course.trainer != request.user:
        return HttpResponseForbidden("You are not the trainer for this course.")
        
    if request.method == 'POST':
        if not assessment.questions.exists():
            messages.error(request, "Cannot publish an assessment with no questions.")
        else:
            assessment.status = 'PUBLISHED'
            assessment.save()
            messages.success(request, "Assessment published successfully!")
            
    return redirect('manage_assessment', assessment_id=assessment.id)