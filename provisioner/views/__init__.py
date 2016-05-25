from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from userservice.user import UserService
from authz_group import Group
from datetime import datetime
import re


def login(request):
    params = {}
    return render_to_response('provisioner/login.html',
                              params,
                              context_instance=RequestContext(request))

def user_is_admin():
    user = UserService().get_original_user()

    netid_match = re.match(
        r'^([^@]+)(@(uw|washington|cac.washington|u.washington).edu)?$', user)
    if netid_match:
        user = netid_match.group(1)

    authz = Group()
    return authz.is_member_of_group(user, settings.MSCA_MANAGER_ADMIN_GROUP)


def _admin(request, template):
    if not user_is_admin():
        return HttpResponseRedirect("/login")

    curr_date = datetime.now().date()

    params = {
        'EVENT_UPDATE_FREQ': settings.ADMIN_EVENT_GRAPH_FREQ,
        'SUBSCRIPTION_UPDATE_FREQ': settings.ADMIN_SUBSCRIPTION_STATUS_FREQ,
        'admin_group': settings.MSCA_MANAGER_ADMIN_GROUP,
    }
    return render_to_response(template, params, RequestContext(request))


@login_required
def ProvisionStatus(request, template='provisioner/status.html'):
    return _admin(request, template)


@login_required
def ManageJobs(request, template='provisioner/jobs.html'):
    return _admin(request, template)
