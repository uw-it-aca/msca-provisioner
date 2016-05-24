from django.core.management.base import BaseCommand, CommandError
from provisioner.subscription import Subscription, \
    Subscription404Exception, SubscriptionBusyException
from json import loads as json_loads
import sys


class Command(BaseCommand):
    help = "Resets test netid"

    def add_arguments(self, parser):
        parser.add_argument('netid', nargs='+')
        parser.add_argument('--subscription',
                            type=int,
                            dest='subscription',
                            default=234,
                            help="subsciption code to reset (default 234)")
        parser.add_argument('--force',
                            dest='force',
                            default=False,
                            help="Force in-process subsciption reset")

    def handle(self, *args, **options):
        try:
            sub = Subscription()
            for netid in options['netid']:
                try:
                    sub.reset(netid, options['subscription'])
                except (Subscription404Exception,
                        SubscriptionBusyException) as err:
                    print >> sys.stderr, "ERROR: %s: %s" % (netid, err)
        except Exception as err:
            raise CommandError('FAIL: %s' % (err))
