from django import forms
from .models import Profile, Certificate, WorkExperience, UserSkill, Skill


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar', 'department', 'phone', 'linkedin_url')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'department': forms.TextInput(attrs={'placeholder': 'e.g. Engineering, HR, Sales'}),
            'phone': forms.TextInput(attrs={'placeholder': '+91 98765 43210'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/yourprofile'}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ('title', 'issued_by', 'issued_date', 'expiry_date', 'file')
        widgets = {
            'issued_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. AWS Solutions Architect'}),
            'issued_by': forms.TextInput(attrs={'placeholder': 'e.g. Amazon Web Services'}),
        }


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ('company', 'role', 'start_date', 'end_date', 'description')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'company': forms.TextInput(attrs={'placeholder': 'Company name'}),
            'role': forms.TextInput(attrs={'placeholder': 'Your job title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief description of responsibilities...'}),
        }


class UserSkillForm(forms.Form):
    """Lets the user pick a skill by name (or create it) and set proficiency."""
    skill_name = forms.CharField(
        max_length=100,
        label='Skill',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Python, Excel, Photoshop'})
    )
    proficiency = forms.ChoiceField(choices=UserSkill.PROFICIENCY_CHOICES)
