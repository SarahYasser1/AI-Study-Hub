import secrets
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import RegisterForm, ProfileForm
from .models import Profile, EmailVerificationToken


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            token = secrets.token_urlsafe(32)
            EmailVerificationToken.objects.create(user=user, token=token)
            verify_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'token': token})
            )
            send_mail(
                subject='Verify your AI Study Hub account',
                message=f'Hi {user.username},\n\nPlease verify your email by clicking:\n{verify_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            login(request, user)
            messages.success(request, 'Welcome! Please check your email to verify your account.')
            return redirect('dashboard:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class StudyHubLoginView(LoginView):
    template_name = 'accounts/login.html'


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


def verify_email_view(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token, used=False)
    profile, _ = Profile.objects.get_or_create(user=token_obj.user)
    profile.email_verified = True
    profile.save()
    token_obj.used = True
    token_obj.save()
    messages.success(request, 'Your email has been verified!')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
