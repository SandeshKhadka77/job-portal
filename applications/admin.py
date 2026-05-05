from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'job', 'email', 'user', 'created_at')
	list_filter = ('created_at', 'job__job_type', 'user')
	search_fields = ('full_name', 'email', 'user__email', 'job__title', 'job__company_name')
	readonly_fields = ('created_at',)
	raw_id_fields = ('user', 'job')
