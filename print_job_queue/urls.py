from django.conf import settings

from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path('jobs/<str:group>/<str:job_type>/', JobQueue.as_view(), name='queue'),
    path('jobs/<str:group>/<str:job_type>/<str:worker_name>', JobQueue.as_view(), name='queue_worker'),

    path('worker/<str:worker_name>/<int:job_id>/pick-up', JobPickUp.as_view(), name='job_pick_up', kwargs={'job_action': 'pick_up'}),
    path('worker/<str:worker_name>/<int:job_id>/print', JobPickUp.as_view(), name='job_print', kwargs={'job_action': 'print'}),
    path('worker/<str:worker_name>/<int:job_id>/mark-completion', JobMarkCompletion.as_view(), name='job_mark_completion'),

    path('job/<int:job_id>/restart', JobRestart.as_view(), name='job_restart'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
