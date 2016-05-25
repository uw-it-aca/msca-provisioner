from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from userservice.user import UserService
from authz_group import Group
from datetime import datetime
import re


class Authorization(object):
    def _validate(self, group):
        user_service = UserService()
        authz = Group()
        user = user_service.get_original_user()
        uwnetid_match = re.match(
            r'^([^@]+)(@(uw|washington|cac.washington|u.washington).edu)?$',
            user)
        if uwnetid_match:
            return authz.is_member_of_group(
                uwnetid_match.group(1), group)

        return authz.is_member_of_group(user, group)

    def is_admin(self):
        return self._validate(settings.MSCA_MANAGER_ADMIN_GROUP)

    def is_support(self):
        return self._validate(settings.MSCA_MANAGER_SUPPORT_GROUP)


def _admin(request, template):
    if not Authorization().is_support():
        return HttpResponseRedirect("/login")

    curr_date = datetime.now().date()

    params = {
        'EVENT_UPDATE_FREQ': settings.ADMIN_EVENT_GRAPH_FREQ,
        'SUBSCRIPTION_UPDATE_FREQ': settings.ADMIN_SUBSCRIPTION_STATUS_FREQ,
        'admin_group': settings.MSCA_MANAGER_ADMIN_GROUP,
    }
    return render_to_response(template, params, RequestContext(request))


def login(request):
    params = {}
    return render_to_response('provisioner/login.html',
                              params,
                              context_instance=RequestContext(request))

@login_required
def ProvisionStatus(request, template='provisioner/status.html'):
    return _admin(request, template)


@login_required
def ManageJobs(request, template='provisioner/jobs.html'):
    return _admin(request, template)
