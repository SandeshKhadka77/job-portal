from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=150, unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    size = models.CharField(max_length=50, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
