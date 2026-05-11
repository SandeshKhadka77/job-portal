from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'get_file_size', 'is_default', 'created_at')
    list_filter = ('is_default', 'created_at', 'user')
    search_fields = ('user__email', 'name')
    readonly_fields = ('created_at', 'updated_at', 'get_file_size_mb', 'get_file_extension')
    fieldsets = (
        ('User & File', {
            'fields': ('user', 'file', 'get_file_extension', 'get_file_size_mb')
        }),
        ('Resume Details', {
            'fields': ('name', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_file_size(self, obj):
        """Display file size in admin list"""
        return f"{obj.get_file_size_mb()} MB"
    get_file_size.short_description = 'File Size'

    def save_model(self, request, obj, form, change):
        """Automatically set user to current user on creation"""
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)
