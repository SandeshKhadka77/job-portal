from django.contrib import admin
from django.utils.html import format_html
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.utils import timezone
from .models import ResumeDownloadLog

import io
import zipfile

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'job', 'email', 'user', 'resume_link', 'status', 'created_at')
	list_filter = ('status', 'created_at', 'job__job_type', 'user')
	search_fields = ('full_name', 'email', 'user__email', 'job__title', 'job__company_name')
	readonly_fields = ('created_at',)
	raw_id_fields = ('user', 'job', 'resume')
	actions = (
		'mark_as_reviewed',
		'mark_as_shortlisted',
		'mark_as_rejected',
		'mark_as_withdrawn',
		'download_resumes',
	)

	@admin.action(description='Mark selected applications as Reviewed')
	def mark_as_reviewed(self, request, queryset):
		updated = queryset.update(status=Application.STATUS_REVIEWED)
		self.message_user(request, f'{updated} application(s) marked as reviewed.')

	@admin.action(description='Mark selected applications as Shortlisted')
	def mark_as_shortlisted(self, request, queryset):
		updated = queryset.update(status=Application.STATUS_SHORTLISTED)
		self.message_user(request, f'{updated} application(s) marked as shortlisted.')

	@admin.action(description='Mark selected applications as Rejected')
	def mark_as_rejected(self, request, queryset):
		updated = queryset.update(status=Application.STATUS_REJECTED)
		self.message_user(request, f'{updated} application(s) marked as rejected.')

	@admin.action(description='Mark selected applications as Withdrawn')
	def mark_as_withdrawn(self, request, queryset):
		updated = queryset.update(status=Application.STATUS_WITHDRAWN)
		self.message_user(request, f'{updated} application(s) marked as withdrawn.')

	def has_resume(self, obj):
		"""Display whether application has an attached resume"""
		return 'Yes' if obj.resume else 'No'
	has_resume.short_description = 'Has Resume'

	def resume_link(self, obj):
		"""Show a link to the attached resume when available"""
		if not obj.resume or not obj.resume.file:
			return '—'
		name = obj.resume.file.name
		if not name or not default_storage.exists(name):
			return 'Missing'
		try:
			url = obj.resume.file.url
			filename = obj.resume.name or obj.resume.file.name.split('/')[-1]
			return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, filename)
		except Exception:
			return 'Unavailable'
	resume_link.short_description = 'Resume'

	@admin.action(description='Download resumes for selected applications')
	def download_resumes(self, request, queryset):
		"""Create a ZIP archive of available resumes for selected applications and return it as a response."""
		buffer = io.BytesIO()
		entries = []
		filenames_list = []
		total_bytes = 0
		for app in queryset.select_related('resume'):
			if not app.resume or not app.resume.file:
				continue
			name = app.resume.file.name
			if not name or not default_storage.exists(name):
				continue
			try:
				with default_storage.open(name, 'rb') as f:
					data = f.read()
				filename = f"{app.full_name.replace(' ', '_')}_{app.pk}_{app.resume.file.name.split('/')[-1]}"
				entries.append((filename, data))
				filenames_list.append(filename)
				total_bytes += len(data)
			except Exception:
				continue

		# enforce configurable limits before creating the ZIP
		max_files = getattr(__import__('django.conf').conf.settings, 'RESUME_DOWNLOAD_MAX_FILES', 50)
		max_total_mb = getattr(__import__('django.conf').conf.settings, 'RESUME_DOWNLOAD_MAX_TOTAL_MB', 100)
		if len(entries) == 0:
			self.message_user(request, 'No resume files found for selected applications.')
			return None
		if len(entries) > max_files:
			self.message_user(request, f'Cannot download {len(entries)} files — limit is {max_files} files per download.')
			return None
		if total_bytes > (max_total_mb * 1024 * 1024):
			self.message_user(request, f'Total resumes size {round(total_bytes/(1024*1024),2)} MB exceeds the allowed {max_total_mb} MB.')
			return None

		added = 0
		with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
			for filename, data in entries:
				zf.writestr(filename, data)
				added += 1

		# record a log entry for the download
		total_mb = round(total_bytes / (1024*1024), 2)
		filenames = ','.join(filenames_list)
		try:
			ResumeDownloadLog.objects.create(
				user=getattr(request, 'user', None),
				applications_count=queryset.count(),
				files_count=added,
				total_size_mb=total_mb,
				filenames=filenames,
			)
		except Exception:
			# non-fatal: log creation failure should not break download
			pass

		buffer.seek(0)
		ts = timezone.now().strftime('%Y%m%d%H%M%S')
		response = HttpResponse(buffer.getvalue(), content_type='application/zip')
		response['Content-Disposition'] = f'attachment; filename=resumes_{ts}.zip'
		return response
