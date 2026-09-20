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
        ('UNVERIFIED', 'Email Not Verified'),
        ('PENDING', 'Pending Approval'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TRAINEE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    otp_secret = models.CharField(max_length=32, blank=True, null=True)

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} - {self.get_role_display()} ({self.get_status_display()})"

from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Invite(models.Model):
    ROLE_CHOICES = [
        ('TRAINER', 'Trainer'),
        ('ADMIN', 'Admin'),
    ]

    email = models.EmailField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invites_sent'
    )
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=3)  # pick your window
        super().save(*args, **kwargs)

    @property
    def status(self):
        if self.used:
            return 'USED'
        if timezone.now() > self.expires_at:
            return 'EXPIRED'
        return 'PENDING'

    def __str__(self):
        return f"{self.email} ({self.role}) - {self.status}"

    @classmethod
    def live_count_for(cls, email):
        return cls.objects.filter(
            email=email,
            used=False,
            expires_at__gt=timezone.now()
        ).count()