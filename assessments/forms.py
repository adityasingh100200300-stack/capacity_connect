from django import forms
from .models import Assessment, Question

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'duration_minutes', 'passing_score', 'deadline']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class QuestionForm(forms.ModelForm):
    options_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter options separated by commas (e.g. Red, Green, Blue)'}),
        help_text="Comma-separated list of choices."
    )

    class Meta:
        model = Question
        fields = ['question_text', 'options_text', 'correct_index', 'weightage']

    def clean_options_text(self):
        text = self.cleaned_data.get('options_text', '')
        # Split by comma, strip whitespace, and remove empty strings
        options = [opt.strip() for opt in text.split(',') if opt.strip()]
        if len(options) < 2:
            raise forms.ValidationError("Please provide at least 2 options.")
        return options

    def clean(self):
        cleaned_data = super().clean()
        options = cleaned_data.get('options_text')
        correct_index = cleaned_data.get('correct_index')

        if options and correct_index is not None:
            if correct_index < 0 or correct_index >= len(options):
                raise forms.ValidationError(f"Correct index must be between 0 and {len(options) - 1}.")
        
        return cleaned_data
