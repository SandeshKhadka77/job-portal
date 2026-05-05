from django.db import models
from django.contrib.auth.models import User

# models
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full-time')
    is_remote = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    
    # Meta options for  admin display 
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'

    # String representation of the model
    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    # Custom method to display salary range
    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f"NRs {self.salary_min:,} - NRs {self.salary_max:,}"
        if self.salary_min:
            return f"From NRs {self.salary_min:,}"
        if self.salary_max:
            return f"Up to NRs {self.salary_max:,}"
        return "Salary not specified"


class UserSavedJob(models.Model):
    """Track which jobs are saved by which users for persistent storage."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by_users')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')  # Prevent duplicate saves
        ordering = ['-saved_at']
        verbose_name = 'User Saved Job'
        verbose_name_plural = 'User Saved Jobs'

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"

