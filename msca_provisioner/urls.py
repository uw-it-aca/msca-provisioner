from django.conf.urls import patterns, include, url
from django.contrib import admin
from provisioner.views import home

urlpatterns = patterns('',
    url(r'^$', home),
    #url(r'^admin/', include(admin.site.urls)),
)
