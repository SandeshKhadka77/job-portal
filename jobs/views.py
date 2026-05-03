from django.shortcuts import render
from .models import Job

# Create your views here.

def home(request):
    featured_jobs = Job.objects.filter(is_featured=True)[:6]
    jobs = featured_jobs if featured_jobs else Job.objects.all()[:6]
    return render(request, 'home.html', {'featured_jobs': jobs})

