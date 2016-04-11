from django.core.management.base import CommandError
from django.conf import settings
from provisioner.management.commands import SISProvisionerCommand
from aws_message.gather import Gather, GatherException
from events.subscription import Subscription, SubscriptionException


class Command(ProvisionerCommand):
    help = "Loads IdReg subscription events from SQS"

    def handle(self, *args, **options):
        try:
            Gather(settings.AWS_SQS.get('SUBSCRIPTION'),
                   Subscription, SubscriptionException).gather_events()
            self.update_job()
        except GatherException as err:
            raise CommandError(err)
        except Exception as err:
            raise CommandError('FAIL: %s' % (err))
