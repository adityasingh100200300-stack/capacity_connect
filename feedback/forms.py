from django import forms
from .models import CourseFeedback


class FeedbackForm(forms.ModelForm):
    RATING_CHOICES = [(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label='Your Rating'
    )

    class Meta:
        model = CourseFeedback
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'What did you think of this course? Any suggestions for improvement?'
            }),
        }
