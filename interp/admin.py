from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.urls.base import reverse
from .models import *
from django.shortcuts import render

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

# class MyModelAdmin(admin.ModelAdmin):
#     def get_urls(self):
#         urls = super(MyModelAdmin, self).get_urls()
#         my_urls = urls('',
#             (r'^send_email/$', self.my_view)
#         )
#         return my_urls + urls


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm
    list_display = ("username", "translate_versions", "country", "language")
    ordering = ("username",)
    actions = ['send_EMAIL']

    fieldsets = (
        (None, {'fields': ('username', 'email','password', 'first_name', 'last_name','language','country')}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email','password', 'first_name', 'last_name','language','country', 'is_superuser', 'is_staff', 'is_active')}
            ),
        )

    filter_horizontal = ()

    def translate_versions(self, obj):
        return '<a href="%s">%s</a>' % (reverse('user_trans', kwargs={'username': obj.username}), 'Translations')

    translate_versions.allow_tags = True

    def send_EMAIL(self, request, queryset):
        from django.core.mail import send_mail
        for i in queryset:
            if i.email:
                send_mail('Subject here', 'Here is the message.', 'milad.ameri73@gmail.com',[i.email], fail_silently=False)
            else:
                self.message_user(request, "Mail sent successfully ")
    send_EMAIL.short_description = "Send an email to selected users"


admin.site.register(FlatPage)
admin.site.register(Task)
admin.site.register(Translation)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Language)
admin.site.register(Country)
admin.site.register(VersionParticle)
admin.site.register(Notification)
admin.site.register(Attachment)