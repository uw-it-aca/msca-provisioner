from django.conf import settings
from restclients.exceptions import DataFailureException
from restclients.uwnetid.subscription import get_netid_subscriptions
from restclients.models.uwnetid import Subscription as NWSSubscription
from provisioner.models import Subscription
from provisioner.resolve import Resolve
from provisioner.exceptions import MSCAProvisionerException
from logging import getLogger


logger = getLogger(__name__)


class License(Resolve):
    def process(self):
        limit = getattr(settings, 'O365_ACTIVATE_PROCESS_LIMIT', 100)
        for activating in Subscription.objects.filter(
                state=Subscription.STATE_ACTIVATE)[:limit]:
            try:
                subscriptions = get_netid_subscriptions(
                    activating.net_id, [activating.subscription])
            except DataFailureException as ex:
                if ex.status == 404:
                    logger.warning('Subscription %s for netid %s does not exist' % (
                        activating.subscription, activating.net_id))
                    continue
                else:
                    raise

            for sub in subscriptions:
                try:
                    if sub.status_code == NWSSubscription.STATUS_PENDING:
                        if self.add_subscription_licensing(activating):
                            activating.state = Subscription.STATE_ACTIVATING
                            self.log.info(
                                'Activating subscription %s for %s' % (
                                    activating.subscription,
                                    activating.net_id))
                        else:
                            activating.state = Subscription.STATE_ACTIVE
                            self.log.info(
                                'Subscription %s for %s already active' % (
                                    activating.subscription,
                                    activating.net_id))

                        activating.save()
                    elif sub.status_code == NWSSubscription.STATUS_CANCELLING:
                        if self.remove_subscription_licensing(activating):
                            activating.state = Subscription.STATE_DELETING
                            self.log.info(
                                'Deactivating subscription %s for %s' % (
                                    activating.subscription,
                                    activating.net_id))
                        else:
                            activating.state = Subscription.STATE_DELETED
                            self.log.info(
                                'Subscription %s for %s already active' % (
                                    activating.subscription,
                                    activating.net_id))

                        activating.save()
                except MSCAProvisionerException as ex:
                    self.log.error("Subscribe: %s" % (ex))
