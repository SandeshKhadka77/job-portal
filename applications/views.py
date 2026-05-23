from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from jobs.models import Job
from accounts.models import Resume
from django.core.files.storage import default_storage

from .models import Application


ACTIVE_APPLICATION_STATUSES = {
	Application.STATUS_SUBMITTED,
	Application.STATUS_REVIEWED,
	Application.STATUS_SHORTLISTED,
}

REAPPLY_ALLOWED_STATUSES = {
	Application.STATUS_WITHDRAWN,
	Application.STATUS_REJECTED,
}


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def apply_job(request, pk):
	job = get_object_or_404(Job, pk=pk)
	user = request.user
	latest_application = (
		Application.objects
		.filter(user=user, job=job)
		.order_by('-created_at')
		.first()
	)
	existing_active_application = (
		Application.objects
		.filter(user=user, job=job, status__in=ACTIVE_APPLICATION_STATUSES)
		.order_by('-created_at')
		.first()
	)
	can_reapply = (
		latest_application is not None and
		existing_active_application is None and
		latest_application.status in REAPPLY_ALLOWED_STATUSES
	)

#  users cannot spam multiple applications for the same job and helps maintain a clean application history.
	if request.method == 'POST':
		if existing_active_application is not None:
			messages.error(request, 'You already have an active application for this job.')
			return redirect('application_detail', pk=existing_active_application.pk)

		if latest_application is not None and latest_application.status not in ACTIVE_APPLICATION_STATUSES and latest_application.status not in REAPPLY_ALLOWED_STATUSES:
			messages.error(request, 'You cannot reapply for this job right now.')
			return redirect('application_detail', pk=latest_application.pk)

		full_name = request.POST.get('full_name', '').strip()
		email = request.POST.get('email', '').strip()
		phone = request.POST.get('phone', '').strip()
		cover_letter = request.POST.get('cover_letter', '').strip()
		resume_id = request.POST.get('resume_id', '').strip()

		if not full_name or not email or not cover_letter:
			messages.error(request, 'Please fill in your name, email, and cover letter.')
		else:
			resume = None
			if resume_id:
				try:
					resume = Resume.objects.get(pk=resume_id, user=user)
				except Resume.DoesNotExist:
					messages.error(request, 'Selected resume is invalid.')
					return redirect('apply_job', pk=job.pk)
			
			Application.objects.create(
				user=user,
				job=job,
				resume=resume,
				full_name=full_name,
				email=email,
				phone=phone,
				cover_letter=cover_letter,
			)
			messages.success(request, 'Your application has been submitted successfully.')
			return redirect('job_detail', pk=job.pk)

	# Get user's resumes for the form
	user_resumes = Resume.objects.filter(user=user)
	default_resume = user_resumes.filter(is_default=True).first()

	# Pre-fill form with user data
	initial_data = {
		'full_name': f'{user.first_name} {user.last_name}'.strip() or user.email,
		'email': user.email,
	}

	return render(request, 'applications/apply.html', {
		'job': job,
		'initial_data': initial_data,
		'existing_active_application': existing_active_application,
		'latest_application': latest_application,
		'can_reapply': can_reapply,
		'user_resumes': user_resumes,
		'default_resume': default_resume,
	})

# allows users to view their job applications with pagination and filtering by status.
@login_required(login_url='login')
@require_http_methods(['GET'])
def my_applications(request):
	status = request.GET.get('status', '').strip()
	page_number = request.GET.get('page', 1)

	applications_qs = (
		Application.objects
		.filter(user=request.user)
		.select_related('job')
		.order_by('-created_at')
	)

	valid_statuses = {choice[0] for choice in Application.STATUS_CHOICES}
	if status in valid_statuses:
		applications_qs = applications_qs.filter(status=status)
	else:
		status = ''

	paginator = Paginator(applications_qs, 6)
	page_obj = paginator.get_page(page_number)

	return render(request, 'applications/my_applications.html', {
		'applications': page_obj.object_list,
		'page_obj': page_obj,
		'status': status,
		'status_choices': Application.STATUS_CHOICES,
	})


@login_required(login_url='login')
@require_http_methods(['GET'])
def application_detail(request, pk):
	application = get_object_or_404(
		Application.objects.select_related('job', 'user'),
		pk=pk,
		user=request.user,
	)

	# Determine whether attached resume file is available in storage
	resume_available = False
	resume_url = None
	resume_filename = None
	resume_size_mb = None
	if application.resume and application.resume.file:
		name = application.resume.file.name
		if name and default_storage.exists(name):
			resume_available = True
			try:
				resume_url = application.resume.file.url
				resume_filename = application.resume.name or application.resume.file.name.split('/')[-1]
				# Use model helper for size when possible
				resume_size_mb = getattr(application.resume, 'get_file_size_mb', None)
				if callable(resume_size_mb):
					resume_size_mb = resume_size_mb()
			except Exception:
				# Fall back to not exposing URL/size if storage doesn't allow access
				resume_url = None
				resume_size_mb = None

	return render(request, 'applications/application_detail.html', {
		'application': application,
		'can_withdraw': application.status in ACTIVE_APPLICATION_STATUSES,
		'resume_available': resume_available,
		'resume_url': resume_url,
		'resume_filename': resume_filename,
		'resume_size_mb': resume_size_mb,
	})


@login_required(login_url='login')
@require_http_methods(['POST'])
def withdraw_application(request, pk):
	application = get_object_or_404(
		Application.objects.select_related('job'),
		pk=pk,
		user=request.user,
	)

	if application.status not in ACTIVE_APPLICATION_STATUSES:
		messages.error(request, 'This application can no longer be withdrawn.')
		return redirect('application_detail', pk=application.pk)

	application.status = Application.STATUS_WITHDRAWN
	application.save(update_fields=['status'])
	messages.success(request, f'Your application for {application.job.title} has been withdrawn.')
	return redirect('application_detail', pk=application.pk)
