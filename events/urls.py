from django.conf.urls import url
from events.views import EventListView

urlpatterns = [
    url(r'api/v1/events/?(?P<begin>[0-9\-:TZtz]+)'
        r'?(?P<end>[0-9\-:TZtz]+)'
        r'?(?P<on>[0-9\-:TZtz]+)'
        r'?(?P<type>\w+)?$', EventListView().run)
]
