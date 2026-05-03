from django.shortcuts import render
from django.db.models import Q
from .models import Job


# Create your views here.

def home(request):
    q = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()

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
        jobs = qs.order_by('-created_at')[:12]

    return render(request, 'home.html', {
        'featured_jobs': jobs,
        'q': q,
        'location': location,
    })

