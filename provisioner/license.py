from django.conf import settings
from restclients.exceptions import DataFailureException
from restclients.uwnetid.subscription import get_netid_subscriptions
from restclients.models.uwnetid import Subscription as NWSSubscription
from provisioner.models import Subscription, SubscriptionCode
from provisioner.resolve import Resolve
from provisioner.exceptions import MSCAProvisionerException


class License(Resolve):
    def process(self):
        limit = settings.O365_LIMITS['process']['default']
        activate = Subscription.objects.filter(
            state=Subscription.STATE_ACTIVATE,
            in_process__isnull=True).values_list('pk', flat=True)[:limit]
        self.log.debug('process subscriptions: %s of %s in process' % (len(activate), limit))
        Subscription.objects.filter(pk__in=list(activate)).update(in_process=True)
        try:
            for activating_pk in activate:
                try:
                    activating = Subscription.objects.get(pk=activating_pk)
                    subscriptions = get_netid_subscriptions(
                        activating.net_id, [activating.subscription])
                    # remember name for later
                    for sub_model in subscriptions:
                        SubscriptionCode.objects.update_or_create(
                            name=sub_model.subscription_name,
                            code=sub_model.subscription_code)
                except DataFailureException as ex:
                    if ex.status == 404:
                        self.log.warning('Subscription %s for netid %s does not exist' % (
                            activating.subscription, activating.net_id))
                        activating.in_process = None
                        activating.save()
                        continue
                    else:
                        raise

                for sub in subscriptions:
                    try:
                        if sub.status_code == NWSSubscription.STATUS_PENDING:
                            activating.state = Subscription.STATE_ACTIVATING
                            if self.add_subscription_licensing(activating):
                                self.log.info(
                                    'Activating subscription %s for %s' % (
                                        activating.subscription,
                                        activating.net_id))
                            else:
                                self.log.info(
                                    'Subscription %s for %s already active' % (
                                        activating.subscription,
                                        activating.net_id))
                        elif sub.status_code == NWSSubscription.STATUS_CANCELLING:
                            activating.state = Subscription.STATE_DELETING
                            if self.remove_subscription_licensing(activating):
                                self.log.info(
                                    'Deactivating subscription %s for %s' % (
                                        activating.subscription,
                                        activating.net_id))
                            else:
                                self.log.info(
                                    'Subscription %s for %s already active' % (
                                        activating.subscription,
                                        activating.net_id))
                    except MSCAProvisionerException as ex:
                        self.log.error("Subscribe: %s" % (ex))

                activating.in_process = None
                activating.save()
        except Exception as ex:
            Subscription.objects.filter(pk__in=list(activate)).update(in_process=None)
            self.log.error('license: fatal error: %s' % (ex))
