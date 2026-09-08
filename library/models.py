from django.db import models
from django.conf import settings


class Resource(models.Model):
    """A file uploaded by a Trainer and accessible to enrolled Trainees."""
    RESOURCE_TYPES = [
        ('VIDEO', 'Recorded Lecture'),
        ('SLIDES', 'Presentation / Slides'),
        ('PDF', 'Study Material / PDF'),
        ('OTHER', 'Other'),
    ]

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='resources'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_resources'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES, default='PDF')
    file = models.FileField(upload_to='library/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()}) — {self.course.title}"

    class Meta:
        ordering = ['-uploaded_at']
