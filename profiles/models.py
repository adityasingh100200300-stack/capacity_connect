from django.db import models
from django.conf import settings


class Profile(models.Model):
    """Extended profile data attached to every user via OneToOne."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    department = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Skill(models.Model):
    """Lookup table of skill/technology names (e.g. 'Python', 'Data Analysis')."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class UserSkill(models.Model):
    """Many-to-many through model linking a user to a skill with a proficiency level."""
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Elementary'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_skills'
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_skills')
    proficiency = models.PositiveSmallIntegerField(choices=PROFICIENCY_CHOICES, default=1)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} — {self.skill.name} ({self.get_proficiency_display()})"


class Certificate(models.Model):
    """Professional certificates uploaded by a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    title = models.CharField(max_length=255)
    issued_by = models.CharField(max_length=255)
    issued_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} — {self.user.username}"

    class Meta:
        ordering = ['-issued_date']


class WorkExperience(models.Model):
    """Work history entries on a user's profile."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='work_experiences'
    )
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if currently employed here")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.role} at {self.company} ({self.user.username})"

    class Meta:
        ordering = ['-start_date']
