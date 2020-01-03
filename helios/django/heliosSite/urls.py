from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import heliosView


urlpatterns = [
    #path(r'', heliosView.index, name = 'index'),
    path(r'', heliosView.heliosView, name = 'index'),
    #path(r'^helios', heliosView.heliosView, name = 'index'),
    path(r'login/', heliosView.loginView, name = 'login'),
    #path(r"^helios/view/", heliosView.heliosView, name = "heliosView")
    #url(r'^redirectlogin/', 'spaweb.views.redirectlogin'),
    #url(r'^(?P<data>[^/]+)/$', views.data, name = 'data'),
]
