from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('TRAINEE', 'Trainee'),
        ('TRAINER', 'Trainer'),
        ('ADMIN', 'Admin'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TRAINEE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.username} - {self.get_role_display()} ({self.get_status_display()})"