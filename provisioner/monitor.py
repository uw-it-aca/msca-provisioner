from django.conf import settings
from provisioner.models import Subscription
from provisioner.resolve import Resolve
from restclients.uwnetid.subscription import modify_subscription_status
from restclients.models.uwnetid import Subscription as NWSSubscription


class Monitor(Resolve):
    def confirm_activation(self):
        limit = settings.O365_LIMITS['monitor']['default']
        subscriptions = Subscription.objects.filter(
            state=Subscription.STATE_ACTIVATING,
            in_process__isnull=True).values_list('pk', flat=True)[:limit]

        Subscription.objects.filter(pk__in=list(subscriptions)).update(in_process=True)

        for sub_pk in subscriptions:
            sub = Subscription.objects.get(pk=sub_pk)
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
                    Subscription.objects.filter(pk__in=list(subscriptions)).update(in_process=None)
                    raise

            sub.in_process = None
            sub.save()

    def confirm_deactivation(self):
        limit = settings.O365_LIMITS['monitor']['default']
        subscriptions = Subscription.objects.filter(
            state=Subscription.STATE_DELETING,
            in_process__isnull=True).values_list('pk', flat=True)[:limit]

        Subscription.objects.filter(pk__in=list(subscriptions)).update(in_process=True)

        for sub_pk in subscriptions:
            sub = Subscription.objects.get(pk=sub_pk)
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
                    Subscription.objects.filter(pk__in=list(subscriptions)).update(in_process=None)
                    raise

            sub.in_process = None
            sub.save()
