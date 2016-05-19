from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from userservice.user import UserService
from authz_group import Group
from datetime import datetime


def login(request):
    params = {}
    return render_to_response('provisioner/login.html',
                              params,
                              context_instance=RequestContext(request))


def _admin(request, template):
    user = UserService().get_original_user()
    authz = Group()
    if not authz.is_member_of_group(user, settings.MSCA_MANAGER_ADMIN_GROUP):
        return HttpResponseRedirect("/")

    curr_date = datetime.now().date()

    params = {
        'EVENT_UPDATE_FREQ': settings.ADMIN_EVENT_GRAPH_FREQ,
        'IMPORT_UPDATE_FREQ': settings.ADMIN_IMPORT_STATUS_FREQ,
        'admin_group': settings.MSCA_MANAGER_ADMIN_GROUP,
    }
    return render_to_response(template, params, RequestContext(request))


@login_required
def ProvisionStatus(request, template='provisioner/status.html'):
    return _admin(request, template)


@login_required
def ManageJobs(request, template='provisioner/jobs.html'):
    return _admin(request, template)