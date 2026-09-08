from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('title', 'body', 'announcement_type', 'is_pinned')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Announcement headline'}),
            'body': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Full announcement content...'
            }),
        }
