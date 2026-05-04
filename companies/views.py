from django.shortcuts import get_object_or_404, render

from jobs.models import Job

from .models import Company

def company_list(request):
    companies = list(Company.objects.all())
    for company in companies:
        company.job_count = Job.objects.filter(company_name__iexact=company.name).count()
    return render(request, 'companies/company_list.html', {'companies': companies})

# The company_detail view retrieves the company based on the provided primary key  and then fetches all jobs associated with that company. 
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    jobs = Job.objects.filter(company_name__iexact=company.name).order_by('-is_featured', '-created_at')
    return render(request, 'companies/company_detail.html', {
        'company': company,
        'jobs': jobs,
    })
