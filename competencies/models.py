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
