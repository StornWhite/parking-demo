# Demo main URL router

from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    # Django Admin
    url(r'^admin/', admin.site.urls),

    # Home page.
    url(r'^$', views.home, name='home'),
]
