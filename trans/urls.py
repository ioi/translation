from django.conf import settings
__author__ = 'MiladDK'

from django.conf.urls import url
from .views import *
from django.conf.urls.static import static


urlpatterns = [
    url(r'^$', FirstPage.as_view(), name='firstpage'),
    url(r'^settings/$', Settings.as_view(), name='settings'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$',Logout.as_view(), name='logout'),

    url(r'^translations/$', Home.as_view(), name='home'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/$', Translations.as_view(), name='question'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/save/$', SaveTranslation.as_view(),
        name='save_translation'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/save_particle/$',
        SaveVersionParticle.as_view(), name='save_version_particle'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/html/$',
        GetTranslatePreview.as_view(), name='gettranspreview'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/markdown$', TranslationMarkdown.as_view(), name='trans_md'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/pdf$', TranslationPDF.as_view(), name='trans_pdf'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/revisions$', Versions.as_view(), name='versions'),
    url(r'^getvers/$', GetVersion.as_view(), name='getVersion'),

    url(r'^getverspar/$', GetVersionParticle.as_view(), name='getVersionParticle'),
    url(r'^preview_translate/(?P<id>[\w]*)/$', TranslatePreview.as_view(), name='preview_translate'),
    url(r'^access_edit_translate/(?P<id>[\w]*)/$', AccessTranslationEdit.as_view(), name='access_edit_translate'),
    url(r'^check_is_editing/(?P<id>[\w]*)/$', CheckTranslationEditAccess.as_view(), name='check_edit_translate'),
    url(r'^finish_edit_translate/(?P<id>[\w]*)/$', FinishTranslate.as_view(), name='finish_trans'),

    url(r'^tasks/$', Tasks.as_view(), name='task'),
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/$', EditTask.as_view(), name='edittask'),
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/save$', SaveTask.as_view(), name='savetask') ,
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/revisions$', TaskVersions.as_view(), name='task_versions'),
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/markdown$$', TaskMarkdown.as_view(), name='task_md'),
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/pdf$', TaskPDF.as_view(), name='task_pdf'),
    url(r'^enabletask/$', EnableTask.as_view(), name='enabletask'),

    url(r'^users/$', UsersList.as_view(), name='users_list'),
    url(r'^user/(?P<username>[\w]*)/$', UserTranslations.as_view(), name='user_trans'),
    url(r'^freeze_trans/(?P<id>[\w]*)/$', FreezeTranslation.as_view(), name='freeze_trans'),
    url(r'^unleash_trans_edit_token/(?P<id>[\w]*)/$', UnleashEditTranslationToken.as_view(), name='unleash_trans_token'),

    url(r'^checkout_version/$', CheckoutVersion.as_view(), name='checkoutversion'),

    url(r'^get_trans_pdf/$', GetTranslatePDF.as_view(), name='gettranspdf'),
    url(r'^mail_trans_pdf/$', MailTranslatePDF.as_view(), name='mailtranspdf'),
    url(r'^print/$', PrintCustomFile.as_view(), name='printcustomfile'),

    url(r'^get_task_pdf/$', GetTaskPDF.as_view(), name='gettaskpdf'),
    url(r'^mail_task_pdf/$', MailTaskPDF.as_view(), name='mailtaskpdf'),
    url(r'^getvers/md/$', GetVersionMarkDown.as_view(), name='get_version_md'),
    url(r'^getvers/pdf/$', GetVersionPDF.as_view(), name='get_version_pdf'),

    url(r'^notifications/$', ReadNotifications.as_view(), name='notifications'),
    url(r'^reset_notifications/$', reset_notifications, name='reset_notifications'),
    url(r'^send_notification/$', SendNotification.as_view(), name='send_notif'),
    url(r'^user/font.css', UserFont.as_view(), name='userfontcss')

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
 + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
