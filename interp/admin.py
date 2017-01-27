from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import *


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm
    list_display = ("username",)
    ordering = ("username",)

    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name', 'last_name','language','country','rtl')}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'first_name', 'last_name','language','country', 'is_superuser', 'is_staff', 'is_active', 'rtl')}
            ),
        )

    filter_horizontal = ()

admin.site.register(Task)
admin.site.register(Translation)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Version)
admin.site.register(Language)
admin.site.register(Country)
admin.site.register(VersionParticle)
admin.site.register(Notification)
