from django.contrib import admin

from .models import *

admin.site.register(Task)
admin.site.register(Translation)
admin.site.register(User)
admin.site.register(Version)
admin.site.register(Language)
admin.site.register(Country)
admin.site.register(VersionParticle)
admin.site.register(Notification)
