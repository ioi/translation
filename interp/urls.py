__author__ = 'MiladDK'

from django.conf.urls import url
from .views import *



urlpatterns = [

    url(r'home/$', Home.as_view(), name='home'),
    url(r'rendered/$', Rendered.as_view(), name='rendered'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^$', FirstPage.as_view(), name='firstpage'),
    url(r'^logout/$',Logout.as_view(), name='logout'),
    url(r'^saveques/$', SaveQuestion.as_view(), name='saveQuestion'),
    url(r'^questions/(?P<id>[\w]*)/$',Questions.as_view(), name='question'),
    url(r'^setting/$', Setting.as_view(), name='setting'),

    # url(r'^/list/$',List.as_view(), name='list'),
    # url(r'^/addtag/$',AddTag.as_view(), name='addtag'),
    # url(r'^/addcomment/$',AddComment.as_view(), name='addcomment'),
    # url(r'^/files/(?P<title>[\w .-]*)/$', Download.as_view(), name='download'),

]
