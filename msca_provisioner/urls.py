from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'provisioner.views', name='home'),
    #url(r'^admin/', include(admin.site.urls)),
)
