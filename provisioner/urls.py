from django.conf.urls import patterns, url, include
from provisioner.views import ManageJobs
from provisioner.views.jobs import JobView, JobListView

urlpatterns = [
    url(r'^jobs$', ManageJobs),
    url(r'api/v1/job/(?P<job_id>[0-9]+)?$', JobView().run),
    url(r'api/v1/jobs/?$', JobListView().run),
]

