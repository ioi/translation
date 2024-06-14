from django.conf import settings

from django.urls import path, re_path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
          path('', FirstPage.as_view(), name='firstpage'),
          path('healthcheck', Healthcheck.as_view(), name='healthcheck'),
          path('settings/', Settings.as_view(), name='settings'),
          path('login/', Login.as_view(), name='login'),
          path('logout/', Logout.as_view(), name='logout'),

          path('home/', Home.as_view(), name='home'),
          re_path(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/$', Translations.as_view(), name='edit'),
          re_path(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/markdown$',
              TranslationMarkdown.as_view(), name='task_md'),
          re_path(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/pdf$',
              TranslationPDF.as_view(), name='task_pdf'),
          re_path(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/print$',
              TranslationPrint.as_view(), name='task_print'),
          re_path(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/revisions$',
              Versions.as_view(), name='revisions'),

          path('getvers/', GetVersion.as_view(), name='getVersion'),
          re_path(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/save/$', SaveTranslation.as_view(),
              name='save_translation'),

          re_path(r'^access_edit_translate/(?P<id>[\w]*)/$', AccessTranslationEdit.as_view(),
              name='access_edit_translate'),
          re_path(r'^finish_edit_translate/(?P<id>[\w]*)/$', FinishTranslate.as_view(), name='finish_trans'),
          re_path(r'^get_latest_translation/(?P<id>[\w]*)/$', GetLatestTranslation.as_view(),
              name='get_latest_translation'),

          re_path(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/release', ReleaseTask.as_view(),
              name='release_task'),
          path('add_task/', AddTask.as_view(), name='add_task'),
          path('revert/', Revert.as_view(), name='revert'),

          path('users/', UsersList.as_view(), name='users_list'),
          re_path(r'^users/(?P<public>[\w]*)/$', UsersList.as_view(), name='public_users_list'),
          re_path(r'^user/(?P<username>[\w-]*)/$', UserTranslations.as_view(), name='user_trans'),
          path('upload_final_pdf/', AddFinalPDF.as_view(), name='upload_final_pdf'),
          re_path(r'^user_freeze_trans/(?P<task_name>[\w]*)/$', UserFreezeTranslation.as_view(), name='user_freeze_trans'),
          re_path(r'^staff_freeze_trans/(?P<task_name>[\w]*)/(?P<username>[\w-]*)/$', StaffFreezeTranslation.as_view(), name='staff_freeze_trans'),
          re_path(r'^freeze_user_contest/(?P<username>[\w-]*)/(?P<contest_id>[\w]*)/$', FreezeUserContest.as_view(),
              name='freeze_user_contest'),
          re_path(r'^unfreeze_user_contest/(?P<username>[\w-]*)/(?P<contest_id>[\w]*)/$',
              UnfreezeUserContest.as_view(), name='unfreeze_user_contest'),
          re_path(r'^seal_user_contest/(?P<username>[\w-]*)/(?P<contest_id>[\w]*)/$',
              SealUserContest.as_view(), name='seal_user_contest'),
          re_path(r'^unleash_edit_token/(?P<id>[\w]*)/$', UnleashEditTranslationToken.as_view(),
              name='unleash_edit_token'),

          path('notifications/', ReadNotifications.as_view(), name='notifications'),
          path('reset_notifications/', reset_notifications, name='reset_notifications'),
          path('send_notification/', SendNotification.as_view(), name='send_notif'),
          re_path(r'^user/(?P<username>[\w-]*)/font.css', UserFont.as_view(), name='userfontcss'),
      ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
