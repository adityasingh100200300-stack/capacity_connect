from django import forms
from .models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'description', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Course title'}),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'What will trainees learn? What are the prerequisites?'
            }),
        }
