import re
import json
from base64 import b64decode
from time import time
from math import floor
import dateutil.parser
from django.conf import settings
from logging import getLogger
from provisioner.models import Subscription as SubscriptionModel
from provisioner.cache import RestClientsCache
from restclients.exceptions import DataFailureException
from events.models import SubscriptionLog
from aws_message.crypto import aes128cbc, Signature, CryptoException
from aws_message.extract import Extract


class SubscriptionException(Exception):
    pass


class Subscription(Extract):
    """
    UW Identity Registration Subscription Event Handler
    """

    # What we expect in a subscription message
    _subscriptionMessageType = 'idreg'
    _subscriptionMessageVersion = 'UWIT-1'

    def __init__(self, settings, message):
        """
        UW IdReg Subscription Event object

        Raises SubscriptionException
        """
        super(Subscription, self).__init__(settings, message)
        self._log = getLogger(__name__)

    def process(self):
        if self._header['messageType'] != self._subscriptionMessageType:
            raise SubscriptionException(
                'Unknown Message Type: %s' % (self._header['messageType']))

        context = json.loads(b64decode(self._header['messageContext']))

        if context['version'] != 'v1':
            raise SubscriptionException(
                'Unknown Subscription version: %s' % (
                    context['version']))

        if context['topic'] != 'subscription':
            self._log.debug('Unknown Subscription topic: %s' % (
                context['topic']))
            return

        subscription = self.extract()
        subscription['subscription'] = int(subscription['subscription'])

        if subscription['subscription'] not in self._settings.get('SUBSCRIPTIONS', {}):
            self._log.debug('Unknown Subscription code: %s' % (
                subscription['subscription']))
            return

        if subscription['type'] in ['insert', 'modify']:
            self._addSubscription(subscription)
        else:
            self._log.debug('Unknown Subscription type: %s' % (
                subscription['type']))

    def _addSubscription(self, subscription):
        try:
            sub = SubscriptionModel.objects.get(
                net_id=subscription['uwnetid'],
                subscription=subscription['subscription'])

            self._log.info('Event %s on %s for %s, processing: %s' % (
                subscription['type'], sub.subscription, sub.net_id, sub.state))

            if not sub.in_process:
                # let license processor figure out what to do
                sub.state = SubscriptionModel.STATE_ACTIVATE
                sub.save()

        except SubscriptionModel.DoesNotExist:
            sub = SubscriptionModel(
                net_id=subscription['uwnetid'],
                subscription=subscription['subscription'],
                state=SubscriptionModel.STATE_ACTIVATE)
            sub.save()

        self._recordSuccess(1)

    def _recordSuccess(self, count):
        minute = int(floor(time() / 60))
        try:
            e = SubscriptionLog.objects.get(minute=minute)
            e.event_count += count
        except SubscriptionLog.DoesNotExist:
            e = SubscriptionLog(minute=minute, event_count=count)

        e.save()

        if e.event_count <= 5:
            limit = self._settings.get('EVENT_COUNT_PRUNE_AFTER_DAY', 7) * 24 * 60
            prune = minute - limit
            SubscriptionLog.objects.filter(minute__lt=prune).delete()
