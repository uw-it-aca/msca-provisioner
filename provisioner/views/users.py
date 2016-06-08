from django.http import HttpResponse
from restclients.o365.user import User
from provisioner.views.rest_dispatch import RESTDispatch
from provisioner.subscription import Subscription as UserSubscription
from provisioner.subscription import NoUserNetidException
from logging import getLogger
from json import dumps as json_dumps
import re


class UserView(RESTDispatch):
    """ Retrieves a User model.
        GET returns 200 with User details.
        PUT returns 200.
    """
    def __init__(self, *args, **kwargs):
        super(UserView, self).__init__(*args, **kwargs)
        self._log = getLogger(__name__)
        self.user_api = User()
        self.user_sub = UserSubscription()

    def GET(self, request, **kwargs):
        if not self.can_request():
            return self.json_response('{"error":"Unauthorized"}', status=401)

        net_id = kwargs['net_id']
        user = self.user_api.get_user_by_netid(net_id)
        return self.json_response(
            json_dumps(self._user_subscriptions(net_id, user)))

    def _user_subscriptions(self, netid, user):
        user_sub = {
            'netid': netid,
            'o365_user': user.json_data(),
            'subscriptions': {}
        }
        try:
            for license in user.assigned_licenses:
                subs = self.user_sub.subscriptions_from_assigned_licenses(
                    netid, user.assigned_licenses)
                for sub in subs:
                    user_sub['subscriptions'][sub.subscription] = sub.state
        except NoUserNetidException:
            pass

        return user_sub


class UserListView(RESTDispatch):
    """ Retrieves User with licenses mapped to configures subscriptions.
    """
    def __init__(self, *args, **kwargs):
        super(UserListView, self).__init__(*args, **kwargs)
        self._log = getLogger(__name__)
        self.user_api = User(per_page=999)
        self.user_sub = UserSubscription()
        self.csv_count = 0
        self.match_count = 0

    def GET(self, request, **kwargs):
        if not self.can_request():
            return self.json_response('{"error":"Unauthorized"}', status=401)

        self._log.info('discovering subscribed office 365 users')
        response = HttpResponse(
            self.user_api.get_users_generator(formatter=self._user_csv),
            content_type="text/csv")
        self._log.info('discovered %s of %s subscribed office 365 users' % (
            self.match_count, self.csv_count))
        return response

    def _user_csv(self, user):
        csv_line = ''
        self.csv_count += 1
        matched = False

        if self.csv_count == 1:
            csv_line = "netid,subcode,state\r\n"
        try:
            netid = self.user_sub.netid_from_user(user)
            if len(user.assigned_licenses):
                subs = self.user_sub.subscriptions_from_assigned_licenses(
                    netid, user.assigned_licenses)
                for sub in subs:
                    csv_line += "%s\r\n" % (','.join([
                        sub.net_id, str(sub.subscription), sub.state]))
                    matched = True
        except NoUserNetidException:
            pass

        if matched:
            self.match_count += 1

        return csv_line
