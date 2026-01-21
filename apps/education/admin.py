from django.contrib import admin

from apps.core.admin_mixins import TenantAdminMixin

from .models import VideoFormation


@admin.register(VideoFormation)
class VideoFormationAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("titre", "langue", "status", "created_at")
    list_filter = ("langue", "status")
