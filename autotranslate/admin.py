from django.contrib import admin
from autotranslate.models import UserTranslationQuota


@admin.register(UserTranslationQuota)
class UserTranslationQuotaAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'credit',
        'used',
    ]
    ordering = ['user']
