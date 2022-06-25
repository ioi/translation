from django.conf import settings

from django.conf.urls import url
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    # Draft job routes.
    url(r'^draft/(?P<group>[\w]*)/$', DraftJobQueue.as_view(), name='draft_queue'),
    url(r'^draft_job_pick_up/(?P<job_id>[\w]*)/$',
        DraftJobPickUp.as_view(),
        name='draft_job_pick_up'),
    url(r'^draft_job_mark_completion/(?P<job_id>[\w]*)/$',
        DraftJobMarkCompletion.as_view(),
        name='draft_job_mark_completion'),

    # Final job routes.
    url(r'^final/(?P<group>[\w]*)/$', FinalJobQueue.as_view(), name='final_queue'),
    url(r'^final_job_pick_up/(?P<job_id>[\w]*)/$',
        FinalJobPickUp.as_view(),
        name='final_job_pick_up'),
    url(r'^final_job_mark_completion/(?P<job_id>[\w]*)/$',
        FinalJobMarkCompletion.as_view(),
        name='final_job_mark_completion'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
