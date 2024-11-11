from django.contrib import admin

from .models import Company


# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "description", "company_email", "owner", "image_path", "created_at", "updated_at")
    list_filter = ("id", "name", "owner", "created_at", "updated_at")
