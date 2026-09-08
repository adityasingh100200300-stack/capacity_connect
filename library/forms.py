from django import forms
from .models import Resource


class ResourceUploadForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('title', 'description', 'resource_type', 'file')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Week 1 - Introduction Slides'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief description of this resource...'}),
        }
