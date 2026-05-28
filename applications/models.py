from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from jobs.models import Job
from accounts.models import Resume


class Application(models.Model):
	STATUS_SUBMITTED = 'submitted'
	STATUS_REVIEWED = 'reviewed'
	STATUS_SHORTLISTED = 'shortlisted'
	STATUS_REJECTED = 'rejected'
	STATUS_WITHDRAWN = 'withdrawn'

	STATUS_CHOICES = [
		(STATUS_SUBMITTED, 'Submitted'),
		(STATUS_REVIEWED, 'Reviewed'),
		(STATUS_SHORTLISTED, 'Shortlisted'),
		(STATUS_REJECTED, 'Rejected'),
		(STATUS_WITHDRAWN, 'Withdrawn'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
	job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
	resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, related_name='applications', null=True, blank=True)
	full_name = models.CharField(max_length=120)
	email = models.EmailField()
	phone = models.CharField(max_length=20, blank=True)
	cover_letter = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.full_name} - {self.job.title}'

class ResumeDownloadLog(models.Model):
    """Log of admin or staff resume bulk downloads."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    applications_count = models.PositiveIntegerField(default=0)
    files_count = models.PositiveIntegerField(default=0)
    total_size_mb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    filenames = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"ResumeDownload by {self.user} at {self.timestamp} ({self.files_count} files)"
