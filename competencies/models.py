from django.db import models
from django.conf import settings
from profiles.models import Skill


class TrainerCompetency(models.Model):
    """
    Summarizes a Trainer's competency in a specific skill area.
    Populated from their UserSkill proficiency scores.
    In Phase 2 this can be auto-computed via a management command or signal.
    """
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='competencies',
        limit_choices_to={'role': 'TRAINER'}
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='trainer_competencies')
    score = models.PositiveSmallIntegerField(
        default=1,
        help_text="1–5 proficiency score, synced from UserSkill or set manually"
    )

    class Meta:
        unique_together = ('trainer', 'skill')
        ordering = ['-score']

    def __str__(self):
        return f"{self.trainer.username} — {self.skill.name} ({self.score}/5)"


# --- Signals for auto-syncing ---
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from profiles.models import UserSkill

@receiver(post_save, sender=UserSkill)
def sync_user_skill_to_trainer_competency(sender, instance, created, **kwargs):
    """
    Whenever a UserSkill is saved, if the user is a TRAINER,
    sync their proficiency score to TrainerCompetency.
    """
    if instance.user.role == 'TRAINER':
        TrainerCompetency.objects.update_or_create(
            trainer=instance.user,
            skill=instance.skill,
            defaults={'score': instance.proficiency}
        )

@receiver(post_delete, sender=UserSkill)
def delete_trainer_competency(sender, instance, **kwargs):
    """
    If a Trainer removes a skill from their profile, remove it from the competency map.
    """
    if instance.user.role == 'TRAINER':
        TrainerCompetency.objects.filter(trainer=instance.user, skill=instance.skill).delete()
