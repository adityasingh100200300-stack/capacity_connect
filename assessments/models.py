from django.db import models # Imports Django's core database relational mapping tools
from django.conf import settings # Imports project settings to safely reference your custom User model

class Assessment(models.Model): # Defines the main container table for a specific quiz
    STATUS_CHOICES = ( # Starts defining the allowed states for the publishing workflow
        ('DRAFT', 'Draft'), # State where trainers can edit without trainees seeing it
        ('PUBLISHED', 'Published'), # State where the quiz is live and locked for taking
        ('ARCHIVED', 'Archived'), # State for old quizzes that are no longer active
    ) # Ends the tuple of state choices

    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assessments') # Links this quiz to the Course model your teammate is building
    title = models.CharField(max_length=255) # Creates a text column for the name of the quiz
    duration_minutes = models.PositiveIntegerField(help_text="Total allowed time in minutes.") # Creates a positive integer column for the strict time limit
    passing_score = models.PositiveIntegerField(default=50) # Sets the default required percentage to pass at 50%
    deadline = models.DateTimeField(help_text="Hard wall-clock deadline.") # Sets an absolute date and time when the quiz closes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT') # Sets the default creation state to Draft

    def __str__(self): # Defines how this object appears as a string in the Python environment
        return f"{self.title} ({self.status})" # Returns the title and status for easy identification in the admin panel

class Question(models.Model): # Defines the table specifically for multiple-choice questions
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions') # Links the question to its parent Assessment container
    question_text = models.TextField() # Creates a large text area column for the actual question prompt
    options = models.JSONField(help_text="List of options as a JSON array") # Stores the multiple choices as a lightweight JSON list (e.g., ["Apple", "Banana", "Cherry"])
    correct_index = models.PositiveSmallIntegerField(help_text="Zero-indexed pointer to the correct option.") # Stores the mathematical index (0, 1, 2) of the right answer securely
    weightage = models.PositiveIntegerField(default=1) # Defines the point value of this specific question for grading calculations

    def __str__(self): # Defines the string representation for the Question object
        return self.question_text[:50] # Returns only the first 50 characters of the question text to keep the admin interface clean

class AssessmentAttempt(models.Model): # Defines the table that tracks a Trainee's active test session
    STATUS_CHOICES = ( # Starts defining the lifecycle states of an attempt session
        ('IN_PROGRESS', 'In Progress'), # State indicating the trainee is currently taking the test and the timer is running
        ('SUBMITTED', 'Submitted'), # State indicating the system has auto-graded the final submission
        ('EXPIRED', 'Expired'), # State indicating the server mathematically determined the trainee ran out of time
    ) # Ends the tuple of attempt choices

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='attempts') # Links the session to the specific quiz being taken
    trainee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attempts') # Links the session to the specific Trainee taking it
    started_at = models.DateTimeField(auto_now_add=True) # Automatically stamps the exact server time when the session is created to start the timer
    submitted_at = models.DateTimeField(null=True, blank=True) # Creates a blank timestamp that will be filled only when the trainee finishes
    score_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Creates a decimal field to hold the final calculated grade percentage
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS') # Sets the default session state to currently running

    class Meta: # Opens the internal Meta class to pass specific database instructions to Django
        unique_together = ('assessment', 'trainee') # Creates a strict database constraint preventing one Trainee from having two concurrent sessions for the same quiz

    def __str__(self): # Defines the string representation for the Attempt object
        return f"{self.trainee.username} - {self.assessment.title}" # Returns a readable string combining the user's name and the quiz title

class AttemptAnswer(models.Model): # Defines the table storing every individual radio-button selection made by the trainee
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='answers') # Links this specific answer back to the active test session
    question = models.ForeignKey(Question, on_delete=models.CASCADE) # Links this answer to the specific multiple-choice question being asked
    selected_index = models.PositiveSmallIntegerField(null=True, blank=True) # Stores the exact numerical index the trainee chose from the JSON array

    def __str__(self): # Defines the string representation for the Answer object
        return f"Answer to {self.question_id} for Attempt {self.attempt_id}" # Returns basic tracking IDs so you can debug the database easily