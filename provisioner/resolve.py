from django.conf import settings
from restclients.o365.license import License, User
from restclients.exceptions import DataFailureException
from provisioner.exceptions import MSCAProvisionerException
from logging import getLogger
from json import loads as json_loads
import re


class Resolve(object):
    def __init__(self, *args, **kwargs):
        self.license_api = License()
        self.user_api = User()
        self.log = getLogger(__name__)
        self.skus = self.license_api.get_subscribed_skus()
        self.licenses = dict((s.sku_part_number, (s.sku_id, dict(
            (p.service_plan_name, p.service_plan_id)
            for p in s.service_plans))) for s in self.skus)

    def subscription_licensing(self, subscription_code):
        """
        Given the subscription code, look up what Office 365 license
        should be applied
        """
        try:
            license_map = settings.O365_LICENSE_MAP[subscription_code]
        except KeyError:
            self.log.error('No license mapping for subscription %s' % (
                subscription_code))
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
                                subscription_code, plan,
                                license_name))

                licenses[self.licenses[license_name][0]] = disabled_plans
            else:
                self.log.warning(
                    'Subcode %s: license %s not in tenant %s subscribed skus' % (
                        subscription_code, license_name,
                        getattr(settings, 'RESTCLIENTS_O365_TENANT', 'test')))

        return licenses

    def licensing_to_assign(self, subscription):
        """return what is left after removing what is assigned
           from what needs to be assigned
        """
        assigned = self.license_api.get_licenses_for_netid(
            subscription.net_id)

        return self.licensing_to_assign_from_assigned(
            subscription.subscription, assigned)

    def licensing_to_assign_from_assigned(self, subscription_code, assigned):
        to_assign = {}
        necessary = self.subscription_licensing(subscription_code)
        for sku_id, disabled_plans in necessary.iteritems():
            assigned_license = [l for l in assigned if sku_id == l.sku_id]
            if len(assigned_license):
                plans = [p for p in disabled_plans if p not in assigned_license[0].disabled_plans]
                if len(plans):
                    to_assign[sku_id] = plans
            else:
                to_assign[sku_id] = list(disabled_plans)

        return to_assign

    def has_subscription_licensing(self, subscription):
        return len(self.licensing_to_assign(subscription)) == 0

    def add_subscription_licensing(self, subscription):
        to_assign = self.licensing_to_assign(subscription)
        return self.set_licensing(subscription.net_id, to_assign)

    def remove_subscription_licensing(self, subscription):
        to_assign = self.subscription_licensing(subscription.subscription)
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
                err_msg = str(ex)
                try:
                    if ex.status == 404:
                        odata = json_loads(ex.msg)['odata.error']
                        err_msg = odata['message']['value']
                        raise MSCAProvisionerNetidNotFound(
                            'License 404: %s: %s' % (netid, err_msg))
                    elif ex.status == 400:
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
                        netid, add, remove, err_msg))

        return False
