from django.conf import settings
from oauth import oauth
import time


class ProvisionerOAuth2Unauthorized(Exception):
    pass


class ProvisionerOAuthConsumer(oauth.OAuthConsumer):
    """
    OAuthConsumer superclass that adds nonce caching
    """
    def __init__(self, key, secret):
        super(ProvisionerOAuthConsumer, self).__init__(key, secret)
        self.nonces = []

    def CheckNonce(self, nonce):
        """
        Returns True if the nonce has been checked in the last hour
        """
        now = time.time()
        old = now - 3600.0
        trim = 0
        for n, t in self.nonces:
            if t < old:
                trim = trim + 1
            else:
                break
        if trim:
            self.nonces = self.nonces[trim:]

        for n, t in self.nonces:
            if n == nonce:
                return True

        self.nonces.append((nonce, now))


class ProvisionerDataStore(oauth.OAuthDataStore):
    """
    Implments model- and settings-based OAuthDataStores
    """
    def lookup_consumer(self, key):
        try:
            consumers = getattr(settings, 'API_CONSUMERS', {})
            return ProvisionerOAuthConsumer(key, consumers[key])
        except KeyError:
            return None

    def lookup_nonce(self, oauth_consumer, oauth_token, nonce):
        return nonce if oauth_consumer.CheckNonce(nonce) else None


class ProvisionerOAuth2(object):
    def __init__(self, request, **kwargs):
        self.request = request
        self.headers = {}
        if 'HTTP_AUTHORIZATION' in request.META:
            self.headers['Authorization'] = request.META.get('HTTP_AUTHORIZATION')
        self.params = dict([(k,v) for k,v in request.GET.iteritems()])
        self.oauth_server = oauth.OAuthServer(
            data_store = ProvisionerDataStore(),
            signature_methods = {
                # Supported signature methods
                'HMAC-SHA1': oauth.OAuthSignatureMethod_HMAC_SHA1()
            })

    def validate(self):
        oauth_request = oauth.OAuthRequest.from_request(
            self.request.method,
            self.request.build_absolute_uri(),
            headers=self.headers,
            parameters=self.params)

        if oauth_request:
            try:
                consumer = self.oauth_server._get_consumer(oauth_request)
                self.oauth_server._check_signature(oauth_request, consumer, None)
                return oauth_request.get_nonoauth_parameters()
            except oauth.OAuthError as err:
                raise ProvisionerOAuth2Unauthorized(err)

        raise ProvisionerOAuth2Unauthorized("NO API ACCESS FOR YOU")
