from django.core.management.base import BaseCommand, CommandError
from provisioner.subscription import Subscription
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
                sub.reset(netid, options['subscription'])
        except Exception as err:
            raise CommandError('FAIL: %s' % (err))
