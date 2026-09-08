from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import CustomUser
from .forms import RegisterForm, LoginForm, UserStatusForm


def register_view(request):
    """Handles new user registration. All accounts start as PENDING."""
    if request.user.is_authenticated:
        return redirect('course_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'TRAINEE':
                messages.success(request, 'Account created! You can now log in.')
            else:
                messages.success(
                    request,
                    'Account created! An administrator will review and approve your account shortly.'
                )
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Authenticates the user and enforces ACTIVE status gate."""
    if request.user.is_authenticated:
        return redirect('course_list')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Gate: block non-ACTIVE users from logging in
            if user.status == 'PENDING':
                messages.warning(request, 'Your account is awaiting admin approval.')
                return render(request, 'accounts/login.html', {'form': form})
            elif user.status == 'REJECTED':
                messages.error(request, 'Your registration was rejected. Contact an administrator.')
                return render(request, 'accounts/login.html', {'form': form})
            elif user.status == 'SUSPENDED':
                messages.error(request, 'Your account has been suspended. Contact an administrator.')
                return render(request, 'accounts/login.html', {'form': form})

            login(request, user)
            next_url = request.GET.get('next', 'course_list')
            return redirect(next_url)
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logs out the user and redirects to the login page."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def pending_users_view(request):
    """Admin-only: lists all pending registration requests."""
    if request.user.role != 'ADMIN':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('course_list')

    pending = CustomUser.objects.filter(status='PENDING').order_by('date_joined')
    all_users = CustomUser.objects.exclude(username=request.user.username).order_by('-date_joined')
    return render(request, 'accounts/pending_users.html', {
        'pending': pending,
        'all_users': all_users,
    })


@login_required
@require_POST
def update_user_status_view(request, user_id):
    """Admin-only: approve or reject a user (POST with 'status' field)."""
    if request.user.role != 'ADMIN':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('course_list')

    target_user = get_object_or_404(CustomUser, id=user_id)
    form = UserStatusForm(request.POST, instance=target_user)
    if form.is_valid():
        form.save()
        messages.success(request, f"User '{target_user.username}' status updated to {target_user.get_status_display()}.")
    else:
        messages.error(request, 'Invalid status value.')

    return redirect('pending_users')
