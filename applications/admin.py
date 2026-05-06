from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'job', 'email', 'user', 'status', 'created_at')
	list_filter = ('status', 'created_at', 'job__job_type', 'user')
	search_fields = ('full_name', 'email', 'user__email', 'job__title', 'job__company_name')
	readonly_fields = ('created_at',)
	raw_id_fields = ('user', 'job')
	actions = (
		'mark_as_reviewed',
		'mark_as_shortlisted',
		'mark_as_rejected',
		'mark_as_withdrawn',
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
