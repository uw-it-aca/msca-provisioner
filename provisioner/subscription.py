from restclients.uwnetid.subscription import modify_subscription_status
from restclients.models.uwnetid import Subscription as NWSSubscription
from restclients.exceptions import DataFailureException
from provisioner.models import Subscription as ProvisionSubscription
from provisioner.resolve import Resolve
from json import loads as json_loads


class Subscription404Exception(Exception): pass
class SubscriptionBusyException(Exception): pass


class Subscription(Resolve):
    def reset(self, netid, subcode):
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
