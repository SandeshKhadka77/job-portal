from django.shortcuts import render
from django.db.models import Q
from .models import Job


# added search and filter functionality to the home view. Users can search by keyword, location, job type, and remote status. If no search parameters are provided, it will show featured jobs or recent jobs as a fallback.

def home(request):
    q = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    job_type = request.GET.get('job_type', '').strip()
    remote = request.GET.get('remote', '').strip()

    # If no search provided, show featured jobs (fallback to recent)
    if not q and not location:
        featured = Job.objects.filter(is_featured=True)
        jobs = featured[:6] if featured.exists() else Job.objects.all()[:6]
    else:
        qs = Job.objects.all()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(company_name__icontains=q)
            )
        if location:
            qs = qs.filter(location__icontains=location)
        if job_type:
            qs = qs.filter(job_type=job_type)
        if remote.lower() in ('1', 'true', 'yes', 'on'):
            qs = qs.filter(is_remote=True)
        jobs = qs.order_by('-created_at')[:12]

    return render(request, 'home.html', {
        'featured_jobs': jobs,
        'q': q,
        'location': location,
        'job_type': job_type,
        'remote': remote,
    })

