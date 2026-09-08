from django.utils import timezone
from .models import AssessmentAttempt

def submit_and_grade_attempt(attempt_id):
    """
    Calculates the final score for an attempt and locks it as SUBMITTED.
    """
    try:
        attempt = AssessmentAttempt.objects.get(id=attempt_id)
    except AssessmentAttempt.DoesNotExist:
        return None
        
    # Prevent re-grading if already submitted or expired
    if attempt.status != 'IN_PROGRESS':
        return attempt
        
    # Fetch all answers tied to this attempt and join the question data
    answers = attempt.answers.select_related('question').all()
    
    total_weight = 0
    earned_weight = 0
    
    for answer in answers:
        weight = answer.question.weightage
        total_weight += weight
        
        # Check if the trainee's choice matches the hidden correct index
        if answer.selected_index == answer.question.correct_index:
            earned_weight += weight
            
    # Calculate the final percentage
    if total_weight > 0:
        attempt.score_percent = round((earned_weight / total_weight) * 100, 2)
    else:
        attempt.score_percent = 0
        
    # Lock the exam session
    attempt.status = 'SUBMITTED'
    attempt.submitted_at = timezone.now()
    attempt.save()
    
    return attempt