from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'size', 'founded_year')
    search_fields = ('name', 'location', 'tagline')
    list_filter = ('location', 'size')
