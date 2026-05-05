from django.contrib import admin
from .models import Job, UserSavedJob

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'location', 'job_type', 'is_featured', 'created_at')
    list_filter = ('job_type', 'is_remote', 'is_featured', 'created_at')
    search_fields = ('title', 'company_name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Job Details', {
            'fields': ('title', 'company_name', 'job_type', 'location')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Salary', {
            'fields': ('salary_min', 'salary_max'),
            'classes': ('collapse',)
        }),
        ('Options', {
            'fields': ('is_remote', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserSavedJob)
class UserSavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at', 'user')
    search_fields = ('user__username', 'job__title', 'job__company_name')
    readonly_fields = ('saved_at',)
    raw_id_fields = ('user', 'job')  # Better UI for foreign key selection
