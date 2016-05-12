from django.conf import settings
from restclients.o365.license import License, User
from restclients.exceptions import DataFailureException
from provisioner.exceptions import MSCAProvisionerException
from logging import getLogger
from json import loads as json_loads
import re


class Resolve(object):
    def __init__(self):
        self.license_api = License()
        self.user_api = User()
        self.log = getLogger(__name__)
        self.skus = self.license_api.get_subscribed_skus()
        self.licenses = dict((s.sku_part_number, (s.sku_id, dict(
            (p.service_plan_name, p.service_plan_id)
            for p in s.service_plans))) for s in self.skus)

    def subscription_licensing(self, subscription):
        """
        Given the subscription code, look up what Office 365 license
        should be applied
        """
        try:
            license_map = settings.O365_LICENSE_MAP[subscription.subscription]
        except KeyError:
            self.log.error('No license mapping for subscription %s' % (
                subscription.subscription))
            return

        licenses = {}
        for license_name, disabled_plans in license_map.iteritems():
            if license_name in self.licenses:
                license_plans = self.licenses[license_name][1]
                disabled_plans = []
                for plan in disabled_plans:
                    if plan in license_plans:
                        disabled_plans.append(license_plans[plan])
                    else:
                        self.log.warning(
                            'Subcode %s: plan %s not part of %s' % (
                                subscription.subscription, plan,
                                license_name))

                licenses[self.licenses[license_name][0]] = disabled_plans
            else:
                self.log.warning(
                    'Subcode %s: license %s not in tenant %s subscribed skus' % (
                        subscription.subscription, license_name,
                        getattr(settings, 'RESTCLIENTS_O365_TENANT', 'test')))

        return licenses

    def licensing_to_assign(self, subscription):
        """return what is left after removing what is assigned
           from what needs to be assigned
        """
        to_assign = self.subscription_licensing(subscription)
        assigned = self.license_api.get_licenses_for_netid(
            subscription.net_id)
        for user_license in assigned:
            try:
                for user_disabled in user_license.disabled_plans:
                    to_assign[user_license.sku_id].remove(user_disabled)

                if len(to_assign[user_license.sku_id]) == 0:
                    del to_assign[user_license.sku_id]
            except ValueError, KeyError:
                continue

        return to_assign

    def has_subscription_licensing(self, subscription):
        return len(self.licensing_to_assign(subscription)) == 0

    def add_subscription_licensing(self, subscription):
        to_assign = self.licensing_to_assign(subscription)
        return self.set_licensing(subscription.net_id, to_assign)

    def remove_subscription_licensing(self, subscription):
        to_assign = self.subscription_licensing(subscription)
        remove = []
        for l in to_assign:
            remove.append(l)

        return self.set_licensing(subscription.net_id, [], remove)

    def set_licensing(self, netid, add=None, remove=None):
        """ Return True if license was set/unset
        """
        if add and len(add) or remove and len(remove):
            try:
                self.license_api.set_licenses_for_netid(
                    netid, add=add, remove=remove)
                return True
            except DataFailureException as ex:
                try:
                    if ex.status == 400:
                        odata = json_loads(ex.msg)['odata.error']
                        code = odata['code']
                        msg = odata['message']['value']
                        if (code == 'Request_BadRequest' and
                            re.match(r'.* invalid usage location\.$', msg)):
                            self.user_api.set_location_for_netid(netid, 'US')
                            self.log.info(
                                'Assigned location "US" to netid %s' % netid)
                            return self.set_licensing(
                                netid, add=add, remove=remove)
                except:
                    pass

                raise MSCAProvisionerException(
                    'License Fail: netid %s: add %s: remove %s: %s' % (
                        netid, add, remove, ex))

        return False
