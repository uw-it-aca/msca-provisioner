from django.conf.urls import url
from provisioner.views import home

urlpatterns = [
    url(r'^$', home, name='home'),
    #url(r'^admin/', include(admin.site.urls)),
]
