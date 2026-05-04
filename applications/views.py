from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from jobs.models import Job

from .models import Application


def apply_job(request, pk):
	job = get_object_or_404(Job, pk=pk)

	if request.method == 'POST':
		full_name = request.POST.get('full_name', '').strip()
		email = request.POST.get('email', '').strip()
		phone = request.POST.get('phone', '').strip()
		cover_letter = request.POST.get('cover_letter', '').strip()

		if not full_name or not email or not cover_letter:
			messages.error(request, 'Please fill in your name, email, and cover letter.')
		else:
			Application.objects.create(
				job=job,
				full_name=full_name,
				email=email,
				phone=phone,
				cover_letter=cover_letter,
			)
			messages.success(request, 'Your application has been submitted successfully.')
			return redirect('job_detail', pk=job.pk)

	return render(request, 'applications/apply.html', {'job': job})
