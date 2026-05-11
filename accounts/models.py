from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_resume_size(file):
    """Validate resume file size (max 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError(f"File size exceeds 5MB limit. Current size: {file.size / (1024*1024):.2f}MB")


class Resume(models.Model):
    """User resume/CV file storage with validation and default selection"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(
        upload_to='resumes/%Y/%m/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'docx', 'doc'],
                message='Only PDF, DOCX, and DOC files are allowed.'
            ),
            validate_resume_size,
        ]
    )
    name = models.CharField(
        max_length=255,
        default='Resume',
        help_text='Give this resume a friendly name (e.g., "Software Engineer Resume")'
    )
    is_default = models.BooleanField(
        default=False,
        help_text='Set as default resume for new applications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'Resume'
        verbose_name_plural = 'Resumes'

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    def save(self, *args, **kwargs):
        """Ensure only one default resume per user"""
        if self.is_default:
            Resume.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def get_file_size_mb(self):
        """Return file size in MB"""
        return round(self.file.size / (1024 * 1024), 2)

    def get_file_extension(self):
        """Return file extension"""
        return self.file.name.split('.')[-1].lower()
