from django.db import models
from django.conf import settings


class Announcement(models.Model):
    """Platform-wide announcement created by an Admin, shown on the homepage."""
    TYPE_CHOICES = [
        ('GENERAL', 'General'),
        ('ACHIEVEMENT', 'Achievement'),
        ('CONTENT', 'New Content'),
        ('NOTIFICATION', 'Notification'),
    ]

    title = models.CharField(max_length=255)
    body = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='GENERAL')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False, help_text="Pinned announcements appear at the top")

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title
