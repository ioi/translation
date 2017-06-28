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

    url(r'^home/$', Home.as_view(), name='home'),
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/$', Translations.as_view(), name='edit'),
    url(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/markdown$', TranslationMarkdown.as_view(), name='trans_md'),
    url(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/pdf$', TranslationPDF.as_view(), name='task_pdf'),
    url(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/html$', TranslationHTML.as_view(), name='task_html'),
    # TODO: add print page
    url(r'^(?P<task_type>[\w]*)/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/print$', TranslationHTML.as_view(), name='task_print'),
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/revisions$', Versions.as_view(), name='versions'),
    url(r'^getvers/$', GetVersion.as_view(), name='getVersion'),
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/save/$', SaveTranslation.as_view(),
        name='save_translation'),
    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/save_particle/$',
        SaveVersionParticle.as_view(), name='save_version_particle'),

    url(r'^getverspar/$', GetVersionParticle.as_view(), name='getVersionParticle'),
    url(r'^access_edit_translate/(?P<id>[\w]*)/$', AccessTranslationEdit.as_view(), name='access_edit_translate'),
    url(r'^check_is_editing/(?P<id>[\w]*)/$', CheckTranslationEditAccess.as_view(), name='check_edit_translate'),
    url(r'^finish_edit_translate/(?P<id>[\w]*)/$', FinishTranslate.as_view(), name='finish_trans'),
    url(r'^get_latest_translation/(?P<id>[\w]*)/$', GetLatestTranslation.as_view(), name='get_latest_translation'),

    url(r'^task/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/release', ReleaseTask.as_view(), name='releasetask') ,
    url(r'^released/(?P<contest_slug>[\w]*)/(?P<task_name>[\w]*)/revisions$', TaskVersions.as_view(), name='task_versions'),
    url(r'^add_task/$', AddTask.as_view(), name='add_task'),

    url(r'^users/$', UsersList.as_view(), name='users_list'),
    url(r'^user/(?P<username>[\w]*)/$', UserTranslations.as_view(), name='user_trans'),
    url(r'^freeze_trans/(?P<id>[\w]*)/$', FreezeTranslation.as_view(), name='freeze_trans'),
    url(r'^unleash_edit_token/(?P<id>[\w]*)/$', UnleashEditTranslationToken.as_view(), name='unleash_edit_token'),

    url(r'^checkout_version/$', CheckoutVersion.as_view(), name='checkoutversion'),

    url(r'^get_task_pdf/$', GetTranslatePDF.as_view(), name='gettranspdf'),
    url(r'^mail_task_pdf/$', MailTranslatePDF.as_view(), name='mailtranspdf'),
    url(r'^print/$', PrintCustomFile.as_view(), name='printcustomfile'),

    url(r'^getvers/md/$', GetVersionMarkDown.as_view(), name='get_version_md'),
    url(r'^getvers/pdf/$', GetVersionPDF.as_view(), name='get_version_pdf'),

    url(r'^notifications/$', ReadNotifications.as_view(), name='notifications'),
    url(r'^reset_notifications/$', reset_notifications, name='reset_notifications'),
    url(r'^send_notification/$', SendNotification.as_view(), name='send_notif'),
    url(r'^user/font.css', UserFont.as_view(), name='userfontcss')

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
 + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
