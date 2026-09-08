from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .models import Profile, Skill, UserSkill, Certificate, WorkExperience
from .forms import ProfileForm, CertificateForm, WorkExperienceForm, UserSkillForm

User = settings.AUTH_USER_MODEL


def _get_or_create_profile(user):
    """Helper: ensures every user has a Profile row."""
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@login_required
def profile_view(request, user_id=None):
    """
    Displays any user's public profile.
    If no user_id is given, shows the logged-in user's own profile.
    """
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()

    if user_id:
        target_user = get_object_or_404(UserModel, id=user_id)
    else:
        target_user = request.user

    profile = _get_or_create_profile(target_user)
    user_skills = UserSkill.objects.filter(user=target_user).select_related('skill')
    certificates = Certificate.objects.filter(user=target_user)
    experiences = WorkExperience.objects.filter(user=target_user)

    is_own_profile = (target_user == request.user)

    return render(request, 'profiles/profile.html', {
        'target_user': target_user,
        'profile': profile,
        'user_skills': user_skills,
        'certificates': certificates,
        'experiences': experiences,
        'is_own_profile': is_own_profile,
    })


@login_required
def edit_profile_view(request):
    """Edit the logged-in user's bio, avatar, and contact info."""
    profile = _get_or_create_profile(request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profiles/edit.html', {'form': form, 'section': 'profile'})


@login_required
def add_certificate_view(request):
    """Upload a new certificate to the user's profile."""
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.user = request.user
            cert.save()
            messages.success(request, 'Certificate added.')
            return redirect('profile_view')
    else:
        form = CertificateForm()

    return render(request, 'profiles/edit.html', {'form': form, 'section': 'certificate'})


@login_required
def add_experience_view(request):
    """Add a work experience entry to the user's profile."""
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            messages.success(request, 'Work experience added.')
            return redirect('profile_view')
    else:
        form = WorkExperienceForm()

    return render(request, 'profiles/edit.html', {'form': form, 'section': 'experience'})


@login_required
def add_skill_view(request):
    """
    Add a skill with proficiency level.
    get_or_create on Skill so we build the lookup table automatically.
    """
    if request.method == 'POST':
        form = UserSkillForm(request.POST)
        if form.is_valid():
            skill_name = form.cleaned_data['skill_name'].strip().title()
            proficiency = form.cleaned_data['proficiency']

            skill, _ = Skill.objects.get_or_create(name=skill_name)
            UserSkill.objects.update_or_create(
                user=request.user,
                skill=skill,
                defaults={'proficiency': proficiency}
            )
            messages.success(request, f'Skill "{skill_name}" saved.')
            return redirect('profile_view')
    else:
        form = UserSkillForm()

    return render(request, 'profiles/edit.html', {'form': form, 'section': 'skill'})


@login_required
def delete_skill_view(request, skill_id):
    """Remove a UserSkill entry from the logged-in user's profile."""
    user_skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    user_skill.delete()
    messages.info(request, 'Skill removed.')
    return redirect('profile_view')
