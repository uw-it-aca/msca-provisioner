from provisioner.models import Subscription
from provisioner.resolve import Resolve
from restclients.uwnetid.subscription import modify_subscription_status
from restclients.models.uwnetid import Subscription as NWSSubscription


class Monitor(Resolve):
    def confirm_activation(self):
        subscriptions = Subscription.objects.filter(
            state=Subscription.STATE_ACTIVATING,
            in_process__isnull=True)
        subscriptions.update(in_process=True)
        for sub in subscriptions:
            if self.has_subscription_licensing(sub):
                try:
                    modify_subscription_status(
                        sub.net_id, sub.subscription,
                        NWSSubscription.STATUS_ACTIVE)
                    self.log.info(
                        'Subscription %s for %s set %s' % (
                            sub.subscription, sub.net_id,
                            NWSSubscription.STATUS_ACTIVE))
                    sub.state = Subscription.STATE_ACTIVE
                    sub.save()
                except:
                    subscriptions.update(in_process=null)
                    raise

            sub.in_process=null
            sub.save()

    def confirm_deactivation(self):
        subscriptions = Subscription.objects.filter(
            state=Subscription.STATE_ACTIVATING,
            in_process__isnull=True)
        subscriptions.update(in_process=True)
        for sub in subscriptions:
            if not self.has_subscription_licensing(sub):
                try:
                    modify_subscription_status(
                        sub.net_id, sub.subscription,
                        NWSSubscription.STATUS_INACTIVE)
                    self.log.info(
                        'Subscription %s for %s set %s' % (
                            sub.subscription, sub.net_id,
                            NWSSubscription.STATUS_INACTIVE))
                    sub.state = Subscription.STATE_DELETED
                    sub.save()
                except:
                    subscriptions.update(in_process=null)
                    raise

            sub.in_process=null
            sub.save()
