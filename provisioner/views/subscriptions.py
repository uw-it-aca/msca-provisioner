from provisioner.models import Subscription, SubscriptionCode
from provisioner.views.rest_dispatch import RESTDispatch
import json


class SubscriptionListView(RESTDispatch):
    """ Retrieves a list of Subscriptions.
    """
    def GET(self, request, **kwargs):
        if not self.is_admin():
            return self.json_response('{"error":"Unauthorized"}', status=401)

        subscriptions = []
        for sub in Subscription.objects.all().order_by('subscription'):
            json_data = sub.json_data()
            json_data['subscription_name'] = None
            try:
                json_data['subscription_name'] = SubscriptionCode.objects.get(
                    code=sub.subscription).name
            except:
                pass

            subscriptions.append(json_data)

        return self.json_response(json.dumps({'subscriptions': subscriptions}))
