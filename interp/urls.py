from django.conf import settings
__author__ = 'MiladDK'

from django.conf.urls import url
from .views import *
from django.conf.urls.static import static


urlpatterns = [

    url(r'home/$', Home.as_view(), name='home'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^add/$', Tasks.as_view(), name='task'),
    url(r'^edittask/(?P<id>[\w]*)/$', EditTask.as_view(), name='edittask'),
    url(r'^savetask/$', SaveTask.as_view(), name='savetask'),
    url(r'^logout/$',Logout.as_view(), name='logout'),
    url(r'^saveques/$', SaveQuestion.as_view(), name='saveQuestion'),
    url(r'^saveverpart/$', SaveVersionParticle.as_view(), name='saveVersionParticle'),
    url(r'^getvers/$', GetVersion.as_view(), name='getVersion'),
    url(r'^getverspar/$', GetVersionParticle.as_view(), name='getVersionParticle'),

    url(r'^versions/(?P<id>[\w]*)/$', Versions.as_view(), name='versions'),
    url(r'^questions/(?P<id>[\w]*)/$',Questions.as_view(), name='question'),
    url(r'^setting/$', Setting.as_view(), name='setting'),
    url(r'^$', FirstPage.as_view(), name='firstpage'),
    url(r'^pdf/$', GeneratePDf.as_view(), name='generatepdf'),
    url(r'^printpdf/$', PrintPDf.as_view(), name='printpdf'),

    url(r'^notifications/$', Notifications.as_view(), name='notifications'),
    url(r'^test/$', Test.as_view(), name='test'),
                  # url(r'^/list/$',List.as_view(), name='list'),
    # url(r'^/addtag/$',AddTag.as_view(), name='addtag'),
    # url(r'^/addcomment/$',AddComment.as_view(), name='addcomment'),
    # url(r'^/files/(?P<title>[\w .-]*)/$', Download.as_view(), name='download'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
