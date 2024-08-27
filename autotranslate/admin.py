from django.contrib import admin
from autotranslate.models import UserTranslationQuota

# Register your models here.
@admin.register(UserTranslationQuota)
class UserTranslationQuotaAdmin(admin.ModelAdmin):
    pass