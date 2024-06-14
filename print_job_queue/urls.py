from django.conf import settings

from django.urls import re_path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    # Draft job routes.
    re_path(r'^draft/(?P<group>[\w]*)/$', DraftJobQueue.as_view(), name='draft_queue'),
    re_path(r'^draft_job_pick_up/(?P<job_id>[\w]*)/$',
        DraftJobPickUp.as_view(),
        name='draft_job_pick_up'),
    re_path(r'^draft_job_mark_completion/(?P<job_id>[\w]*)/$',
        DraftJobMarkCompletion.as_view(),
        name='draft_job_mark_completion'),

    # Final job routes.
    re_path(r'^final/(?P<group>[\w]*)/$', FinalJobQueue.as_view(), name='final_queue'),
    re_path(r'^final_job_pick_up/(?P<job_id>[\w]*)/$',
        FinalJobPickUp.as_view(),
        name='final_job_pick_up'),
    re_path(r'^final_job_mark_completion/(?P<job_id>[\w]*)/$',
        FinalJobMarkCompletion.as_view(),
        name='final_job_mark_completion'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
