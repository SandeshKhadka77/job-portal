from django.db import models

from jobs.models import Job


class Application(models.Model):
	job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
	full_name = models.CharField(max_length=120)
	email = models.EmailField()
	phone = models.CharField(max_length=20, blank=True)
	cover_letter = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.full_name} - {self.job.title}'
