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

    attempt, created = AssessmentAttempt.objects.get_or_create(
        assessment=assessment,
        trainee=request.user,
        defaults={'status': 'IN_PROGRESS'}
    )

    if attempt.status != 'IN_PROGRESS':
        return redirect('assessment_result', attempt_id=attempt.id)

    return redirect('take_assessment', attempt_id=attempt.id)


@login_required
def take_assessment(request, attempt_id):
    """Renders the exam and enforces the strict time limit upon submission."""
    attempt = get_object_or_404(AssessmentAttempt, id=attempt_id, trainee=request.user)

    if attempt.status != 'IN_PROGRESS':
        return redirect('assessment_result', attempt_id=attempt.id)

    elapsed_seconds = (timezone.now() - attempt.started_at).total_seconds()
    allowed_seconds = attempt.assessment.duration_minutes * 60

    if request.method == 'POST' or elapsed_seconds > (allowed_seconds + 30):
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

# Replace add_question and edit_question in assessments/views.py with these.
# Everything else in the file (start_assessment, take_assessment,
# assessment_result, create_assessment, manage_assessment,
# publish_assessment, delete_question) stays exactly as it is.


def _extract_options_and_correct(request):
    """Shared parsing/validation for the dynamic option rows. Returns
    (options, correct_index, error) — error is None if everything's valid."""
    options = [o.strip() for o in request.POST.getlist('options') if o.strip()]
    correct_option = request.POST.get('correct_option')

    if len(options) < 2:
        return options, None, "Please provide at least 2 options."
    if correct_option is None or correct_option == '':
        return options, None, "Select which option is correct."

    correct_index = int(correct_option)
    if not (0 <= correct_index < len(options)):
        return options, None, "The selected correct answer doesn't match the options given."

    return options, correct_index, None


@login_required
def add_question(request, assessment_id):
    """On validation failure, re-renders manage.html with the bound form,
    the error message, and — importantly — the trainer's typed options and
    their correct-answer selection, so nothing gets lost."""
    assessment = get_object_or_404(Assessment, id=assessment_id)

    if assessment.course.trainer != request.user:
        return HttpResponseForbidden("You are not the trainer for this course.")

    if assessment.status != 'DRAFT':
        return HttpResponseForbidden("Cannot modify questions after publishing.")

    error = None
    submitted_options = None
    submitted_correct = None

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        options, correct_index, error = _extract_options_and_correct(request)
        submitted_options = options
        submitted_correct = request.POST.get('correct_option')

        if form.is_valid() and error is None:
            question = form.save(commit=False)
            question.assessment = assessment
            question.options = options
            question.correct_index = correct_index
            question.save()
            messages.success(request, "Question added successfully.")
            return redirect('manage_assessment', assessment_id=assessment.id)
    else:
        form = QuestionForm()

    questions = assessment.questions.all()
    return render(request, 'assessments/manage.html', {
        'assessment': assessment,
        'questions': questions,
        'form': form,
        'error': error,
        'submitted_options': submitted_options,
        'submitted_correct': submitted_correct,
    })


@login_required
def edit_question(request, question_id):
    """Edit an existing question. DRAFT-only."""
    question = get_object_or_404(Question, id=question_id)
    assessment = question.assessment

    if assessment.course.trainer != request.user:
        return HttpResponseForbidden("You are not the trainer for this course.")

    if assessment.status != 'DRAFT':
        messages.error(request, "Published assessments cannot be edited.")
        return redirect('manage_assessment', assessment_id=assessment.id)

    error = None

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        options, correct_index, error = _extract_options_and_correct(request)

        if form.is_valid() and error is None:
            q = form.save(commit=False)
            q.options = options
            q.correct_index = correct_index
            q.save()
            messages.success(request, "Question updated successfully.")
            return redirect('manage_assessment', assessment_id=assessment.id)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'assessments/edit_question.html', {
        'assessment': assessment,
        'question': question,
        'form': form,
        'error': error,
    })

@login_required
def delete_question(request, question_id):
    """Delete a question. DRAFT-only."""
    question = get_object_or_404(Question, id=question_id)
    assessment = question.assessment

    if assessment.course.trainer != request.user:
        return HttpResponseForbidden("You are not the trainer for this course.")

    if assessment.status != 'DRAFT':
        messages.error(request, "Published assessments cannot be modified.")
        return redirect('manage_assessment', assessment_id=assessment.id)

    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question deleted successfully.")

    return redirect('manage_assessment', assessment_id=assessment.id)