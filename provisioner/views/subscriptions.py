from provisioner.models import Subscription, SubscriptionCode
from provisioner.views.rest_dispatch import RESTDispatch
from provisioner.views import user_is_admin
from django.db.models import Q
import json


class SubscriptionListView(RESTDispatch):
    """ Retrieves a list of Subscriptions.
    """
    def GET(self, request, **kwargs):
        if not user_is_admin():
            return self.json_response('{"error":"Unauthorized"}', status=401)

        subscriptions = []
        default_states = [
            Subscription.STATE_ACTIVATE,
            Subscription.STATE_ACTIVATING,
            Subscription.STATE_DELETING
        ]

        query = request.GET.get('state')
        query_states = query.split(',') if query and len(query.strip()) else default_states
        model_filter = self._model_filter(query_states)
        if model_filter:
            for sub in Subscription.objects.filter(model_filter).order_by('subscription'):
                json_data = sub.json_data()
                json_data['subscription_name'] = None
                try:
                    json_data['subscription_name'] = SubscriptionCode.objects.get(
                        code=sub.subscription).name
                except:
                    pass

                subscriptions.append(json_data)

        if Subscription.STATE_ACTIVE in query_states:
            # poll tenent for all active users
            pass

        if Subscription.STATE_DELETED in query_states:
            # poll tenent for all active users
            pass

        return self.json_response(json.dumps({'subscriptions': subscriptions}))

    def _model_filter(self, states):
        filter = None

        for state in states:
            if state in [
                    Subscription.STATE_ACTIVATE,
                    Subscription.STATE_ACTIVATING,
                    Subscription.STATE_DELETE,
                    Subscription.STATE_ACTIVE, # REMOVE FOR FLIGHT
                    Subscription.STATE_DELETING,
                    Subscription.STATE_DELETED, # REMOVE FOR FLIGHT
                    Subscription.STATE_PENDING,
                    Subscription.STATE_FAILED,
                    Subscription.STATE_DISUSER
            ]:
                if filter:
                    filter |= Q(state=state)
                else:
                    filter = Q(state=state)

        return filter if len(filter) else None
