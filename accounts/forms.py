from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    """Sign-up form — exposes role selection but excludes ADMIN (set via django-admin)."""
    ALLOWED_ROLES = [
        ('TRAINEE', 'Trainee'),
        ('TRAINER', 'Trainer'),
    ]
    role = forms.ChoiceField(choices=ALLOWED_ROLES, initial='TRAINEE')
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # All new registrations start as PENDING until an Admin approves
        user.status = 'PENDING'
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Standard login — validation of ACTIVE status happens in the view."""
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class UserStatusForm(forms.ModelForm):
    """Admin form for approving or rejecting a pending user."""
    class Meta:
        model = CustomUser
        fields = ('status',)
