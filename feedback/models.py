from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class CourseFeedback(models.Model):
    """A Trainee's rating and comment on a Course. One per trainee per course."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 (Poor) to 5 (Excellent)"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.course.title} ({self.rating}★)"
