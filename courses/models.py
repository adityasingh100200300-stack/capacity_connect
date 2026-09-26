from django.db import models
from django.conf import settings


class Course(models.Model):
    """A training course created and managed by a Trainer."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'role': 'TRAINER'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Unpublish to hide from trainees")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Enrollment(models.Model):
    """Records a Trainee's enrollment in a Course."""
    trainee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'TRAINEE'}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('trainee', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.trainee.username} → {self.course.title}" 
 
class Doubt(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='doubts')
    trainee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doubts_raised')
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.title} ({self.course.title})"
 
 
class DoubtComment(models.Model):
    doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doubt_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['created_at']
 
    def __str__(self):
        return f"Comment by {self.author} on {self.doubt_id}"


from django.conf import settings
from django.db import models
from django.utils import timezone


class TraineeStreak(models.Model):
    """One row per trainee. Advanced lazily — only updated when record_engagement()
    is called from an actual action (resource download, assessment attempt,
    doubt post/reply). Not touched by login alone."""
    trainee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak',
        limit_choices_to={'role': 'TRAINEE'}
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.trainee.username}: {self.current_streak}-day streak"

    @property
    def display_streak(self):
        """What to show in templates — current_streak on its own can be stale
        if the trainee missed a day but hasn't triggered a re-check yet."""
        if not self.last_active_date:
            return 0
        gap = (timezone.localdate() - self.last_active_date).days
        return self.current_streak if gap <= 1 else 0


class Achievement(models.Model):
    """A badge definition. Rows are created on-the-fly by streaks.py the first
    time a milestone is hit, so you don't need to pre-populate this table."""
    code = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=10, default='🏆')

    def __str__(self):
        return self.title


class TraineeAchievement(models.Model):
    trainee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trainee', 'achievement')
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.trainee.username} — {self.achievement.title}"

    # Add to courses/models.py. Assumes Question/Assessment are already in this
# file (they are, per what you pasted). No changes to those two models needed.

from django.conf import settings
from django.db import models


class PracticeOnlyQuestion(models.Model):
    """A question that only ever exists for practice — never part of a real,
    graded Assessment. Trainer-authored, freely reusable across sessions."""
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='practice_only_questions')
    question_text = models.TextField()
    options = models.JSONField(help_text="List of options as a JSON array")
    correct_index = models.PositiveSmallIntegerField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'TRAINER'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50]


class PracticeSession(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='practice_sessions')
    trainee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_count = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)   # live, in-session counter
    best_streak = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.trainee.username} — {self.course.title} practice"


class PracticeSessionQuestion(models.Model):
    """A single question served within a session. Snapshots the text/options/
    answer at serve-time — deliberately NOT a live FK to Question or
    PracticeOnlyQuestion, so editing/deleting the source later never
    corrupts a trainee's past practice history."""
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name='items')
    order = models.PositiveIntegerField()
    question_text = models.TextField()
    options = models.JSONField()
    correct_index = models.PositiveSmallIntegerField()
    selected_index = models.PositiveSmallIntegerField(null=True, blank=True)
    timed_out = models.BooleanField(default=False)
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    @property
    def is_correct(self):
        return (not self.timed_out) and self.selected_index == self.correct_index