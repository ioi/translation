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
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_title>[\w]*)/$', Translations.as_view(), name='question'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_title>[\w]*)/save/$', SaveTranslation.as_view(),
        name='save_translation'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_title>[\w]*)/save_particle/$',
        SaveVersionParticle.as_view(), name='save_version_particle'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_title>[\w]*)/html/$',
        GetTranslatePreview.as_view(), name='gettranspreview'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_title>[\w]*)/md$', TranslationMarkdown.as_view(), name='trans_md'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_title>[\w]*)/pdf$', TranslationPDF.as_view(), name='trans_pdf'),
    url(r'^translation/(?P<contest_slug>[\w]*)/(?P<task_title>[\w]*)/revesions$', Versions.as_view(), name='versions'),
    url(r'^getvers/$', GetVersion.as_view(), name='getVersion'),

    url(r'^getverspar/$', GetVersionParticle.as_view(), name='getVersionParticle'),
    url(r'^preview_translate/(?P<id>[\w]*)/$', TranslatePreview.as_view(), name='preview_translate'),
    url(r'^access_edit_translate/(?P<id>[\w]*)/$', AccessTranslationEdit.as_view(), name='access_edit_translate'),
    url(r'^check_is_editing/(?P<id>[\w]*)/$', CheckTranslationEditAccess.as_view(), name='check_edit_translate'),
    url(r'^versions/(?P<id>[\w]*)/$', Versions.as_view(), name='versions'),
    
    url(r'^tasks/$', Tasks.as_view(), name='task'),
    url(r'^task/(?P<id>[\w]*)/$', EditTask.as_view(), name='edittask'),
    url(r'^task_versions/(?P<id>[\w]*)/$', TaskVersions.as_view(), name='taskVersions'),
    url(r'^savetask/$', SaveTask.as_view(), name='savetask') ,
    url(r'^enabletask/$', EnableTask.as_view(), name='enabletask'),

    url(r'^users/$', UsersList.as_view(), name='users_list'),
    url(r'^user/(?P<username>[\w]*)/$', UserTranslations.as_view(), name='user_trans'),
    url(r'^freeze_trans/(?P<id>[\w]*)/$', FreezeTranslation.as_view(), name='freeze_trans'),
    url(r'^unleash_trans_edit_token/(?P<id>[\w]*)/$', UnleashEditTranslationToken.as_view(), name='unleash_trans_token'),

    url(r'^checkout_version/$', CheckoutVersion.as_view(), name='checkoutversion'),

    url(r'^get_trans_pdf/$', GetTranslatePDF.as_view(), name='gettranspdf'),
    url(r'^mail_trans_pdf/$', MailTranslatePDF.as_view(), name='mailtranspdf'),
    url(r'^print_custom_file/$', PrintCustomFile.as_view(), name='printcustomfile'),

    url(r'^get_task_pdf/$', GetTaskPDF.as_view(), name='gettaskpdf'),
    url(r'^mail_task_pdf/$', MailTaskPDF.as_view(), name='mailtaskpdf'),
    url(r'^getvers/md/$', GetVersionMarkDown.as_view(), name='get_version_md'),
    url(r'^getvers/pdf/$', GetVersionPDF.as_view(), name='get_version_pdf'),

    url(r'^notifications/$', Notifications.as_view(), name='notifications'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
 + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
