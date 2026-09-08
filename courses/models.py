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