from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Invite


class RegisterForm(UserCreationForm):
    """Trainee self-registration only. Trainer/Admin come in via invite links."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@cap.com'):
            raise forms.ValidationError("Registration is restricted to organizational members. Your email must end with '@cap.com'.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = 'TRAINEE'
        user.status = 'UNVERIFIED'

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


class InviteForm(forms.Form):
    ROLE_CHOICES = [
        ('TRAINER', 'Trainer'),
        ('ADMIN', 'Admin'),
    ]
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@cap.com'):
            raise forms.ValidationError("Invites can only be sent to organizational emails ending with '@cap.com'.")
        if Invite.live_count_for(email) >= 2:
            raise forms.ValidationError("This email already has 2 pending invites. Wait for one to expire or be used.")
        return email


class InviteRegisterForm(UserCreationForm):
    """Used only via a valid invite link — email and role are fixed by the invite, not user input."""
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')
class InviteRegisterForm(UserCreationForm):
    """Used only via a valid invite link — email and role are fixed by the invite, not user input."""
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})