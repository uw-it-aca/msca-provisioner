from django.conf import settings
from restclients.exceptions import DataFailureException
from restclients.uwnetid.subscription import get_netid_subscriptions
from restclients.models.uwnetid import Subscription as NWSSubscription
from provisioner.models import Subscription, SubscriptionCode
from provisioner.resolve import Resolve
from provisioner.exceptions import MSCAProvisionerException, \
    MSCAProvisionerNetidNotFound


class LicenseAlreadyAppropriate(Exception):
    """Exception for licensing already set/cleared"""
    pass


class UninterestingSubscriptionState(Exception):
    """Exception for ignored subscription states"""
    pass


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
                    subscription = get_netid_subscriptions(
                        activating.net_id, [activating.subscription])[0]
                    # remember name for later
                    SubscriptionCode.objects.update_or_create(
                        name=subscription.subscription_name,
                        code=subscription.subscription_code)
                except DataFailureException as ex:
                    if ex.status == 404:
                        self.log.warning('Subscription %s for netid %s does not exist' % (
                            activating.subscription, activating.net_id))
                        activating.in_process = None
                        activating.save()
                        continue
                    else:
                        raise

                try:
                    if subscription.status_code == NWSSubscription.STATUS_PENDING:
                        if self.add_subscription_licensing(activating):
                            activating.state = Subscription.STATE_ACTIVATING
                            self.log.info(
                                'Activating subscription %s for %s' % (
                                    activating.subscription,
                                    activating.net_id))
                        else:
                            raise LicenseAlreadyAppropriate()
                    elif subscription.status_code == NWSSubscription.STATUS_CANCELLING:
                        if self.remove_subscription_licensing(activating):
                            activating.state = Subscription.STATE_DELETING
                            self.log.info(
                                'Deactivating subscription %s for %s' % (
                                    activating.subscription,
                                    activating.net_id))
                        else:
                            raise LicenseAlreadyAppropriate()
                    else:
                        raise UninterestingSubscriptionState()

                    activating.in_process = None
                    activating.save()

                except UninterestingSubscriptionState:
                    self.log.info(
                        'Subscription %s for %s state %s ignored' % (
                            activating.subscription,
                            activating.net_id,
                            subscription.status_code))
                    activating.delete()
                except LicenseAlreadyAppropriate:
                    self.log.info(
                        'Subscription %s for %s appropriately licensed for %s' % (
                            activating.net_id,
                            activating.subscription,
                            subscription.status_code))
                    activating.delete()
                except MSCAProvisionerNetidNotFound as ex:
                    if subscription.status_code == NWSSubscription.STATUS_PENDING:
                        self.log.error("Retry activate %s for %s later: %s" % (
                            activating.subscription, activating.net_id, ex))
                        activating.in_process = None
                        activating.save()
                    elif subscription.status_code == NWSSubscription.STATUS_CANCELLING:
                        self.log.error("Deactivate: no netid %s with %s: %s" % (
                            activating.net_id, activating.subscription, ex))
                        activating.delete()
                except MSCAProvisionerException as ex:
                    self.log.error("License subcode %s for %s: %s" % (
                        activating.subscription, activating.net_id, ex))

        except Exception as ex:
            Subscription.objects.filter(pk__in=list(activate)).update(in_process=None)
            self.log.error('license: fatal error: %s' % (ex))
