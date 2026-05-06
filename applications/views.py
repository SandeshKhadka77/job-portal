from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from jobs.models import Job

from .models import Application


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def apply_job(request, pk):
	job = get_object_or_404(Job, pk=pk)
	user = request.user

	if request.method == 'POST':
		full_name = request.POST.get('full_name', '').strip()
		email = request.POST.get('email', '').strip()
		phone = request.POST.get('phone', '').strip()
		cover_letter = request.POST.get('cover_letter', '').strip()

		if not full_name or not email or not cover_letter:
			messages.error(request, 'Please fill in your name, email, and cover letter.')
		else:
			Application.objects.create(
				user=user,
				job=job,
				full_name=full_name,
				email=email,
				phone=phone,
				cover_letter=cover_letter,
			)
			messages.success(request, 'Your application has been submitted successfully.')
			return redirect('job_detail', pk=job.pk)

	# Pre-fill form with user data
	initial_data = {
		'full_name': f'{user.first_name} {user.last_name}'.strip() or user.email,
		'email': user.email,
	}

	return render(request, 'applications/apply.html', {
		'job': job,
		'initial_data': initial_data
	})


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
