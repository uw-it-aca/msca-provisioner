from django.conf.urls import include, url
from provisioner.views import ProvisionStatus, login


urlpatterns = [
    url(r'^$', ProvisionStatus, name='home'),
    url(r'login.*', login),
    url(r'^events/', include('events.urls')),
    url(r'^provisioner/', include('provisioner.urls')),
]
