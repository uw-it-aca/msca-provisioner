from django.conf import settings
from aws_message.gather import Gather, GatherException
from events.subscription import Subscription, SubscriptionException
from logging import getLogger


class Loader(object):
    def __init__(self):
        """Loads IdReg subscription events from SQS
        """
        self._log = getLogger(__name__)

    def load_subscription_events(self):
        try:
            Gather(settings.AWS_SQS.get('SUBSCRIPTION'),
                   Subscription,
                   SubscriptionException).gather_events()
        except GatherException as eex:
            self._log.error('Subscription Event Loader: %s' % (ex))
