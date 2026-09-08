from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Assessment, AssessmentAttempt, AttemptAnswer
from .services import submit_and_grade_attempt

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