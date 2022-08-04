from django.conf import settings

from django.conf.urls import url
from .views import *
from django.conf.urls.static import static

urlpatterns = [
          url(r'^$', FirstPage.as_view(), name='firstpage'),
          url(r'^healthcheck$', Healthcheck.as_view(), name='healthcheck'),
          url(r'^settings/$', Settings.as_view(), name='settings'),
          url(r'^login/$', Login.as_view(), name='login'),
          url(r'^logout/$', Logout.as_view(), name='logout'),

          url(r'^home/$', Home.as_view(), name='home'),
          url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/$', Translations.as_view(), name='edit'),
          url(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/markdown$',
              TranslationMarkdown.as_view(), name='task_md'),
          url(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/pdf$',
              TranslationPDF.as_view(), name='task_pdf'),
          url(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/print$',
              TranslationPrint.as_view(), name='task_print'),
          url(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/revisions$',
              Versions.as_view(), name='revisions'),

          url(r'^getvers/$', GetVersion.as_view(), name='getVersion'),
          url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/save/$', SaveTranslation.as_view(),
              name='save_translation'),

          url(r'^access_edit_translate/(?P<id>[\w]*)/$', AccessTranslationEdit.as_view(),
              name='access_edit_translate'),
          url(r'^finish_edit_translate/(?P<id>[\w]*)/$', FinishTranslate.as_view(), name='finish_trans'),
          url(r'^get_latest_translation/(?P<id>[\w]*)/$', GetLatestTranslation.as_view(),
              name='get_latest_translation'),

          url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/release', ReleaseTask.as_view(),
              name='release_task'),
          url(r'^add_task/$', AddTask.as_view(), name='add_task'),
          url(r'^revert/$', Revert.as_view(), name='revert'),

          url(r'^users/$', UsersList.as_view(), name='users_list'),
          url(r'^users/(?P<public>[\w]*)/$', UsersList.as_view(), name='public_users_list'),
          url(r'^user/(?P<username>[\w-]*)/$', UserTranslations.as_view(), name='user_trans'),
          url(r'^upload_final_pdf/$', AddFinalPDF.as_view(), name='upload_final_pdf'),
          url(r'^user_freeze_trans/(?P<task_name>[\w]*)/$', UserFreezeTranslation.as_view(), name='user_freeze_trans'),
          url(r'^staff_freeze_trans/(?P<task_name>[\w]*)/(?P<username>[\w-]*)/$', StaffFreezeTranslation.as_view(), name='staff_freeze_trans'),
          url(r'^freeze_user_contest/(?P<username>[\w-]*)/(?P<contest_id>[\w]*)/$', FreezeUserContest.as_view(),
              name='freeze_user_contest'),
          url(r'^unfreeze_user_contest/(?P<username>[\w-]*)/(?P<contest_id>[\w]*)/$',
              UnfreezeUserContest.as_view(), name='unfreeze_user_contest'),
          url(r'^seal_user_contest/(?P<username>[\w-]*)/(?P<contest_id>[\w]*)/$',
              SealUserContest.as_view(), name='seal_user_contest'),
          url(r'^unleash_edit_token/(?P<id>[\w]*)/$', UnleashEditTranslationToken.as_view(),
              name='unleash_edit_token'),

          url(r'^notifications/$', ReadNotifications.as_view(), name='notifications'),
          url(r'^reset_notifications/$', reset_notifications, name='reset_notifications'),
          url(r'^send_notification/$', SendNotification.as_view(), name='send_notif'),
          url(r'^user/(?P<username>[\w-]*)/font.css', UserFont.as_view(), name='userfontcss'),
      ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
