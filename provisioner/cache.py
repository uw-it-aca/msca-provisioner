from restclients.cache_implementation import TimedCache
from restclients.models import CacheEntryTimed
import re


class RestClientsCache(TimedCache):
    """ A custom cache implementation for MSCA Provisioner """

    kws_url_current_key = '/key/v1/type/%s/encryption/current'
    kws_url_key = '/key/v1/encryption/%s.json'

    url_policies = {}
    url_policies["kws"] = (
        (re.compile(r"^%s" % (
            kws_url_key % '[\-\da-fA-F]{36}\\')), 60 * 60 * 24 * 30),
        (re.compile(r"^%s" % (
            kws_url_current_key % "[\-\da-zA-Z]+")), 60 * 60 * 24 * 7),
    )

    def deleteCache(self, service, url):
        try:
            entry = CacheEntryTimed.objects.get(service=service, url=url)
            entry.delete()
        except CacheEntryTimed.DoesNotExist:
            return

    def delete_cached_kws_current_key(self, resource_type):
        self.deleteCache('kws', self.kws_url_current_key % resource_type)

    def delete_cached_kws_key(self, key_id):
        self.deleteCache('kws', self.kws_url_key % key_id)

    def _get_cache_policy(self, service, url):
        for policy in RestClientsCache.url_policies.get(service, []):
            if policy[0].match(url):
                return policy[1]
        return 0

    def getCache(self, service, url, headers):
        cache_policy = self._get_cache_policy(service, url)
        return self._response_from_cache(service, url, headers, cache_policy)

    def processResponse(self, service, url, response):
        if self._get_cache_policy(service, url):
            return self._process_response(service, url, response)
