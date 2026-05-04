from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect
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

# added job_detail view to display the details of a specific job. 
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    saved_job_ids = request.session.get('saved_job_ids', [])
    related_jobs = (
        Job.objects.exclude(pk=job.pk)
        .filter(location__icontains=job.location.split(',')[0])
        .order_by('-is_featured', '-created_at')[:3]
    )

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'related_jobs': related_jobs,
        'is_saved': job.pk in saved_job_ids,
    })

# added toggle_saved_job view to allow users to save or unsave jobs. 
def toggle_saved_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    saved_job_ids = request.session.get('saved_job_ids', [])

    if pk in saved_job_ids:
        saved_job_ids.remove(pk)
        messages.success(request, f'Removed {job.title} from saved jobs.')
    else:
        saved_job_ids.append(pk)
        messages.success(request, f'Saved {job.title} for later.')

    request.session['saved_job_ids'] = saved_job_ids
    request.session.modified = True
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('job_detail', pk=pk)


def saved_jobs(request):
    saved_job_ids = request.session.get('saved_job_ids', [])
    saved_job_map = {job.pk: job for job in Job.objects.filter(pk__in=saved_job_ids)}
    saved_job_list = [saved_job_map[job_id] for job_id in saved_job_ids if job_id in saved_job_map]

    return render(request, 'jobs/saved_jobs.html', {'saved_jobs': saved_job_list})

