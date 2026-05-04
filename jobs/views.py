from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Job


# added search and filter functionality to the home view. Users can search by keyword, location, job type, and remote status. If no search parameters are provided, it will show featured jobs or recent jobs as a fallback.

def home(request):
    q = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    job_type = request.GET.get('job_type', '').strip()
    remote = request.GET.get('remote', '').strip()
    page_number = request.GET.get('page', 1)

    # Default to all jobs, with featured roles shown first.
    jobs = Job.objects.all().order_by('-is_featured', '-created_at')

    if q or location or job_type or remote:
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
        jobs = qs.order_by('-is_featured', '-created_at')

    paginator = Paginator(jobs, 6)
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'home.html', {
        'featured_jobs': page_obj.object_list,
        'page_obj': page_obj,
        'q': q,
        'location': location,
        'job_type': job_type,
        'remote': remote,
        'query_params': query_params.urlencode(),
    })

