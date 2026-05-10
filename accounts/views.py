from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Count
from .forms import RegisterForm, LoginForm
from jobs.models import UserSavedJob, Job
from applications.models import Application


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Migrate session-based saved jobs to database
            saved_job_ids = request.session.get('saved_job_ids', [])
            if saved_job_ids:
                for job_id in saved_job_ids:
                    try:
                        job = Job.objects.get(pk=job_id)
                        UserSavedJob.objects.get_or_create(user=user, job=job)
                    except Job.DoesNotExist:
                        pass
                del request.session['saved_job_ids']
                messages.info(request, 'Your saved jobs have been migrated to your account.')
            
            # Auto-login the new user
            login(request, user)
            messages.success(request, f'Welcome {user.first_name or user.email}! Your account has been created.')
            return redirect('profile')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Find user by email (username is set to email)
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    
                    # Migrate session-based saved jobs to database
                    saved_job_ids = request.session.get('saved_job_ids', [])
                    if saved_job_ids:
                        for job_id in saved_job_ids:
                            try:
                                job = Job.objects.get(pk=job_id)
                                UserSavedJob.objects.get_or_create(user=user, job=job)
                            except Job.DoesNotExist:
                                pass
                        del request.session['saved_job_ids']
                        messages.info(request, 'Your saved jobs have been synced to your account.')
                    
                    messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                    next_page = request.GET.get('next', 'profile')
                    return redirect(next_page)
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Profile view to display user information, saved jobs count, and applications count.
@login_required(login_url='login')
def profile_view(request):
    user = request.user
    saved_jobs_count = UserSavedJob.objects.filter(user=user).count()
    applications_count = user.applications.count()
    saved_jobs = UserSavedJob.objects.filter(user=user).select_related('job').order_by('-saved_at')[:5]
    recent_applications = user.applications.select_related('job').order_by('-created_at')[:5]
   
    # Aggregate application counts by status for dashboard
    status_counts_qs = (
        Application.objects
        .filter(user=user)
        .values('status')
        .annotate(count=Count('id'))
    )
    status_counts = {item['status']: item['count'] for item in status_counts_qs}

    # Build summary list preserving the display order
    status_summary = [
        (key, label, status_counts.get(key, 0))
        for key, label in Application.STATUS_CHOICES
    ]

    return render(request, 'accounts/profile.html', {
        'saved_jobs_count': saved_jobs_count,
        'applications_count': applications_count,
        'recent_saved_jobs': saved_jobs,
        'recent_applications': recent_applications,
        'status_summary': status_summary,
    })

