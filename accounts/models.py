from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('status', 'ACTIVE')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

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

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} - {self.get_role_display()} ({self.get_status_display()})"