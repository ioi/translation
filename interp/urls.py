from django.conf import settings
__author__ = 'MiladDK'

from django.conf.urls import url
from .views import *
from django.conf.urls.static import static


urlpatterns = [

    url(r'home/$', Home.as_view(), name='home'),
    url(r'user_trans/(?P<username>[\w]*)/$', UserTranslations.as_view(), name='user_trans'),
    url(r'freeze_trans/(?P<id>[\w]*)/$', FreezeTranslation.as_view(), name='freeze_trans'),
    url(r'unleash_trans_edit_token/(?P<id>[\w]*)/$', UnleashEditTranslationToken.as_view(), name='unleash_trans_token'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^task/$', Tasks.as_view(), name='task'),

    url(r'^edittask/(?P<id>[\w]*)/$', EditTask.as_view(), name='edittask'),
    url(r'^savetask/$', SaveTask.as_view(), name='savetask'),
    url(r'^publishtask/$', PublishTask.as_view(), name='publishtask'),
    url(r'^logout/$',Logout.as_view(), name='logout'),
    url(r'^saveques/$', SaveQuestion.as_view(), name='saveQuestion'),
    url(r'^saveverpart/$', SaveVersionParticle.as_view(), name='saveVersionParticle'),
    url(r'^getvers/$', GetVersion.as_view(), name='getVersion'),
    url(r'^getvers/md/$', GetVersionMarkDown.as_view(), name='get_version_md'),
    url(r'^getvers/pdf/$', GetVersionPDF.as_view(), name='get_version_pdf'),
    url(r'^getverspar/$', GetVersionParticle.as_view(), name='getVersionParticle'),

    url(r'^preview_translate/(?P<id>[\w]*)/$',TranslatePreview.as_view(), name='preview_translate'),
    url(r'^access_edit_translate/(?P<id>[\w]*)/$', AccessTranslationEdit.as_view(), name='access_edit_translate'),
    url(r'^check_is_editing/(?P<id>[\w]*)/$', CheckTranslationEditAccess.as_view(), name='check_edit_translate'),
    url(r'^versions/(?P<id>[\w]*)/$', Versions.as_view(), name='versions'),
    url(r'^task_versions/(?P<id>[\w]*)/$', TaskVersions.as_view(), name='taskVersions'),
    url(r'^questions/(?P<id>[\w]*)/$',Questions.as_view(), name='question'),
    url(r'^setting/$', Setting.as_view(), name='setting'),
    url(r'^$', FirstPage.as_view(), name='firstpage'),
    url(r'^get_trans_pdf/$', GetTranslatePDF.as_view(), name='gettranspdf'),
    url(r'^mail_trans_pdf/$', MailTranslatePDF.as_view(), name='mailtranspdf'),
    url(r'^get_trans_preview/$', GetTranslatePreview.as_view(), name='gettranspreview'),
    url(r'^get_task_pdf/$', GetTaskPDF.as_view(), name='gettaskpdf'),
    url(r'^mail_task_pdf/$', MailTaskPDF.as_view(), name='mailtaskpdf'),

    url(r'^notifications/$', Notifications.as_view(), name='notifications'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
 + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
