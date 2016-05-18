from time import time, gmtime, mktime, strftime, localtime
from calendar import timegm
from math import floor
import dateutil.parser
from django.conf import settings
from django.http import HttpResponse
from provisioner.views.rest_dispatch import RESTDispatch
from events.models import SubscriptionLog
from logging import getLogger
import json


log = getLogger('events.enrollment')


class EventListView(RESTDispatch):
    """
    Expose ranges of event counts
    """
    def GET(self, request, **kwargs):
        try:
            event_type = request.GET.get('type', 'enrollment')
            start_sample = int(floor(time() / 60))  # default to now
            end_sample = start_sample

            utc_str = request.GET.get('on')
            if utc_str is not None:
                start_sample = self._start_minutes(utc_str)
                end_sample = start_sample
            else:
                utc_str = request.GET.get('begin')
                if utc_str is not None:
                    start_sample = self._start_minutes(utc_str)
                    utc_str = request.GET.get('end')
                    if utc_str is not None:
                        end_sample = self._start_minutes(utc_str)
                        if (start_sample > end_sample):
                            t = start_sample
                            start_sample = end_sample
                            end_sample = t

            events = {
                'start': strftime("%Y-%m-%dT%H:%M:%SZ", gmtime(start_sample * 60)),
                'end': strftime("%Y-%m-%dT%H:%M:%SZ", gmtime(end_sample * 60)),
                'points': [0 for i in xrange((end_sample - start_sample + 1))]
            }

            if event_type == 'subscription':
                event_log = SubscriptionLog.objects.filter(
                    minute__gte=start_sample
                )
            else:
                raise Exception('unknown event type %s' % event_type)

            for o in event_log:
                try:
                    events['points'][o.minute - start_sample] = o.event_count
                except:
                    pass

            return self.json_response(json.dumps(events))
        except Exception as err:
            return self.json_response('{"error":"Invalid event search %s"}' % (
                err), status=404)

    def _start_minutes(self, utc_str):
        utc = dateutil.parser.parse(utc_str)
        return int(floor(timegm(utc.timetuple()) / 60))
