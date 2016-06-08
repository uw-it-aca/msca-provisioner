from django.conf import settings
from restclients.uwnetid.subscription import modify_subscription_status
from restclients.o365.user import User
from restclients.models.uwnetid import Subscription as NWSSubscription
from restclients.exceptions import DataFailureException
from provisioner.models import Subscription as ProvisionSubscription
from provisioner.resolve import Resolve
from json import loads as json_loads
import re


class Subscription404Exception(Exception):
    pass


class SubscriptionBusyException(Exception):
    pass


class NoUserNetidException(Exception):
    pass


class Subscription(Resolve):
    def __init__(self, *args, **kwargs):
        super(Subscription, self).__init__(*args, **kwargs)
        self._re_netid = re.compile(
            r'^([^@]+)@%s$' % settings.RESTCLIENTS_O365_PRINCIPLE_DOMAIAN)

    def netid_from_user(self, user):
        match = self._re_netid.match(user.user_principal_name)
        if not match:
            raise NoUserNetidException()

        return match.group(1)

    def subscriptions_from_assigned_licenses(self, netid, licenses):
        subscriptions = []
        for code, plans in settings.O365_LICENSE_MAP.iteritems():
            l = self.licensing_to_assign_from_assigned(code, licenses)
            if not len(l):
                subscriptions.append(ProvisionSubscription(
                    net_id=netid, subscription=code,
                    state=ProvisionSubscription.STATE_ACTIVE))

        return subscriptions

    def reprovision(self, netid, subcode):
        try:
            try:
                sub = ProvisionSubscription.objects.get(
                    net_id=netid, subscription=subcode,
                    state=ProvisionSubscription.STATE_ACTIVE)
                if sub.in_process:
                    raise SubscriptionBusyException(
                        "Cannot reset: %s subcode %s in process" % (
                            netid, subcode))

            except ProvisionSubscription.DoesNotExist:
                sub = ProvisionSubscription(
                    net_id=netid, subscription=subcode,
                    state=ProvisionSubscription.STATE_ACTIVE)

            if self.has_subscription_licensing(sub):
                self.log.info('reset: removing licensing for %s subcode %s' % (
                    netid, subcode))
                self.remove_subscription_licensing(sub)

            if sub.id:
                sub.delete()

            modify_subscription_status(
                netid, subcode, NWSSubscription.STATUS_PENDING)

            self.log.info('reset: set subcode %s for %s %s' % (
                subcode, netid, NWSSubscription.STATUS_PENDING))
        except DataFailureException as ex:
            if ex.status == 404:
                try:
                    odata = json_loads(ex.msg)['odata.error']
                    err_msg = odata['message']['value']
                except:
                    err_msg = str(ex)

                raise Subscription404Exception('%s' % (err_msg))

            raise ex
