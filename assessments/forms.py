from django import forms
from .models import Assessment, Question


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'duration_minutes', 'passing_score', 'deadline']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()


class QuestionForm(forms.ModelForm):
    """Only handles question_text now. Options and which one is correct come
    from dynamic option rows in the template (options[] + correct_option in
    POST), validated manually in the view — a plain comma-separated field
    can't cleanly represent "N free-text inputs + pick one" without forcing
    the trainer to count indexes by hand, which was the actual problem.
    weightage is intentionally left out of the form: every question defaults
    to 1 at the model level, so there's no per-question knob to expose, but
    the field stays on the model in case grading logic elsewhere reads it."""

    class Meta:
        model = Question
        fields = ['question_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()