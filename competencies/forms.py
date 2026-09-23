from django import forms
from .models import TrainerCompetency


class TrainerCompetencyForm(forms.ModelForm):
    """
    Allows a trainer to manually adjust their competency score for a skill.
    Only the score field is editable — trainer and skill are set by context.
    """
    class Meta:
        model = TrainerCompetency
        fields = ['score']
        widgets = {
            'score': forms.Select(
                choices=[(i, f"{i} — {label}") for i, label in [
                    (1, 'Beginner'),
                    (2, 'Elementary'),
                    (3, 'Intermediate'),
                    (4, 'Advanced'),
                    (5, 'Expert'),
                ]],
                attrs={'class': 'form-control'},
            ),
        }
        labels = {
            'score': 'Proficiency Level',
        }
