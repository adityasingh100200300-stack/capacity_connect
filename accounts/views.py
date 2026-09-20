from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import CustomUser
from .forms import RegisterForm, LoginForm, UserStatusForm

import pyotp

from django.db import models

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import InviteForm
from .models import Invite

def register_view(request):
    """Trainee self-registration. Account created UNVERIFIED until OTP is confirmed."""
    if request.user.is_authenticated:
        return redirect('course_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            otp_secret = pyotp.random_base32()
            user.otp_secret = otp_secret
            user.save(update_fields=['otp_secret'])

            totp = pyotp.TOTP(otp_secret, interval=300)  # code valid for 5 minutes
            code = totp.now()

            send_mail(
                subject='Verify your Capacity Connect account',
                message=f'Your verification code is: {code}\n\nThis code expires in 5 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            request.session['unverified_user_id'] = user.id
            return redirect('verify_otp')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_otp_view(request):
    user_id = request.session.get('unverified_user_id')
    if not user_id:
        messages.error(request, 'Nothing to verify. Please register first.')
        return redirect('register')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        totp = pyotp.TOTP(user.otp_secret, interval=300)

        if totp.verify(code, valid_window=1):
            user.status = 'ACTIVE'
            user.otp_secret = None
            user.save(update_fields=['status', 'otp_secret'])
            del request.session['unverified_user_id']
            messages.success(request, 'Email verified! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid or expired code. Please try again.')

    return render(request, 'accounts/verify_otp.html', {'email': user.email})

def login_view(request):
    """Authenticates the user and enforces ACTIVE status gate."""
    if request.user.is_authenticated:
        return redirect('course_list')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Gate: block non-ACTIVE users from logging in
            if user.status=='UNVERIFIED':
                messages.warning(request, 'Please verify your email before logging in.')
                return render(request, 'accounts/login.html', {'form': form})
            elif user.status == 'PENDING':
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

def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'

@login_required
@user_passes_test(is_admin)
def send_invite(request):
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            invite = Invite.objects.create(
                email=form.cleaned_data['email'],
                role=form.cleaned_data['role'],
                invited_by=request.user
            )

            signer = signing.TimestampSigner()
            raw_token = signer.sign(f"{invite.email}:{invite.role}:{invite.id}")
            invite.token = raw_token
            invite.save(update_fields=['token'])

            invite_link = request.build_absolute_uri(
                reverse('invite_signup', kwargs={'token': raw_token})
            )

            send_mail(
                subject='You have been invited to Capacity Connect',
                message=f'You have been invited as a {invite.get_role_display()}.\n\n'
                        f'Complete your registration here:\n{invite_link}\n\n'
                        f'This link expires on {invite.expires_at.strftime("%d %b %Y")}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invite.email],
            )
            return redirect('send_invite')
    else:
        form = InviteForm()

    return render(request, 'accounts/send_invite.html', {'form': form})

from django.core.signing import BadSignature, SignatureExpired
from django.shortcuts import get_object_or_404
from .forms import InviteRegisterForm

def invite_signup(request, token):
    try:
        signer = signing.TimestampSigner()
        unsigned = signer.unsign(token)  # no max_age here — expiry is checked via the Invite row itself
        email, role, invite_id = unsigned.rsplit(':', 2)
    except BadSignature:
        return render(request, 'accounts/invite_invalid.html', {'reason': 'This invite link is invalid.'})

    invite = get_object_or_404(Invite, id=invite_id, token=token)

    if invite.status != 'PENDING':
        return render(request, 'accounts/invite_invalid.html', {'reason': f'This invite is {invite.status.lower()}.'})

    if request.method == 'POST':
        form = InviteRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = invite.email
            user.role = invite.role
            user.save()

            invite.used = True
            invite.save(update_fields=['used'])

            return redirect('login')
    else:
        form = InviteRegisterForm()

    return render(request, 'accounts/invite_signup.html', {
        'form': form,
        'email': invite.email,
        'role': invite.get_role_display(),
    })

def resend_otp_view(request):
    """Lets an UNVERIFIED user get a new code, whether or not their session survived."""
    if request.method == 'POST':
        identifier = request.POST.get('username_or_email', '').strip()
        user = CustomUser.objects.filter(
            models.Q(username=identifier) | models.Q(email=identifier),
            status='UNVERIFIED'
        ).first()

        if user:
            otp_secret = pyotp.random_base32()
            user.otp_secret = otp_secret
            user.save(update_fields=['otp_secret'])

            totp = pyotp.TOTP(otp_secret, interval=300)
            send_mail(
                subject='Your new Capacity Connect verification code',
                message=f'Your verification code is: {totp.now()}\n\nThis code expires in 5 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            request.session['unverified_user_id'] = user.id

        # Same message whether or not a match was found — don't reveal which usernames/emails exist
        messages.success(request, 'If that account needs verification, a new code has been sent.')
        return redirect('verify_otp')

    return render(request, 'accounts/resend_otp.html')