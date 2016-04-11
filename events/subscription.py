import re
import json
from base64 import b64decode
from time import time
from math import floor
import dateutil.parser
from django.conf import settings
from django.utils.log import getLogger
from provisioner.models import Subscription as SubscriptionModel
from provisioner.cache import RestClientsCache
from restclients.kws import KWS
from restclients.exceptions import DataFailureException
from events.models import SubscriptionLog
from aws_message.crypto import aes128cbc, Signature, CryptoException


class SubscriptionException(Exception):
    pass


class Subscription(object):
    """
    UW Identity Registration Subscription Event Handler
    """

    # What we expect in a subscription message
    _subscriptionMessageType = 'idreg-v1-subscription'
    _subscriptionMessageVersion = '1'

    _header = None
    _body = None

    def __init__(self, settings, message):
        """
        UW IdReg Subscription Event object

        Raises SubscriptionException
        """
        self._kws = KWS()
        self._settings = settings
        self._message = message
        self._header = message['Header']
        self._body = message['Body']
        self._re_guid = re.compile(r'^[\da-f]{8}(-[\da-f]{4}){3}-[\da-f]{12}$', re.I)
        if self._header['MessageType'] != self._subscriptionMessageType:
            raise SubscriptionException(
                'Unknown Message Type: %s' % (self._header['MessageType']))

        self._log = getLogger(__name__)

    def process(self):
        if self._settings.get('VALIDATE_MSG_SIGNATURE', True):
            self.validate()

        subscriptions = 0
        for event in self._extract()['Events']:
            if event['context']['version'] != 'v1':
                raise SubscriptionException(
                    'Unknown Subscription version: %s' % (
                        event['context']['version']))

            if event['context']['topic'] != 'subcription':
                raise SubscriptionException(
                    'Unknown Subscription topic: %s' % (
                        event['context']['topic']))

            subcription = int(event['subscription'])

            try:
                SubscriptionModel.objects.get(
                    net_id=event['uwnetid'],
                    subscription=subscription)

            except SubscriptionModel.DoesNotExist:
                sub = SubscriptionModel(
                    net_id=event['uwnetid'],
                    subscription=subscription,
                    state=STATE_INITIAL)
                sub.save()
                subscriptions += 1
                                        
        self._recordSuccess(subscriptions)

    def validate(self):
        t = self._header['Version']
        if t != self._subscriptionMessageVersion:
            raise SubscriptionException('Unknown Version: ' + t)

        to_sign = self._header['MessageType'] + '\n' \
            + self._header['MessageId'] + '\n' \
            + self._header['TimeStamp'] + '\n' \
            + self._body + '\n'

        sig_conf = {
            'cert': {
                'type': 'url',
                'reference': self._header['SigningCertURL']
            }
        }

        try:
            Signature(sig_conf).validate(to_sign.encode('ascii'),
                                         b64decode(self._header['Signature']))
        except CryptoException as err:
            raise SubscriptionException('Crypto: %s' % (err))
        except Exception as err:
            raise SubscriptionException('Invalid signature: %s' % (err))

    def _extract(self):
        try:
            t = self._header['Encoding']
            if str(t).lower() != 'base64':
                raise SubscriptionException('Unkown encoding: ' + t)

            t = self._header.get('Algorithm', 'aes128cbc')
            if str(t).lower() != 'aes128cbc':
                raise SubscriptionException('Unsupported algorithm: ' + t)

            # regex removes cruft around JSON
            rx = re.compile(r'[^{]*({.*})[^}]*')
            key_id = self._header['KeyId']
            if key_id and re.match(self._re_guid, key_id):
                key = self._kws.get_key(key_id).key
                body = self._decryptBody(key)
            else:
                try:
                    key = self._kws.get_current_key(
                        self._header['MessageType']).key
                    body = self._decryptBody(key)
                    # look like json?
                    if not re.match(r'^\s*{.+}\s*$', body):
                        raise CryptoException()
                except (ValueError, CryptoException) as err:
                    RestClientsCache().delete_cached_kws_current_key(
                        self._header['MessageType'])
                    key = self._kws.get_current_key(
                        self._header['MessageType']).key
                    body = self._decryptBody(key)

            return(json.loads(rx.sub(r'\g<1>', body)))
        except KeyError as err:
            self._log.error("Key Error: %s\nHEADER: %s" % (err, self._header));
            raise
        except (ValueError, CryptoException) as err:
            raise SubscriptionException('Cannot decrypt: %s' % (err))
        except DataFailureException as err:
            msg = "Request failure for %s: %s (%s)" % (
                self.url, self.msg, self.status)
            self._log.error(msg)
            raise SubscriptionException(msg)
        except Exception as err:
            raise SubscriptionException('Cannot read: %s' % (err))

    def _decryptBody(self, key):
        cipher = aes128cbc(b64decode(key), b64decode(self._header['IV']))
        return cipher.decrypt(b64decode(self._body))

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
