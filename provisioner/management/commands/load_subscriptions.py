from django.core.management.base import CommandError
from provisioner.management.commands import ProvisionerCommand
from provisioner.loader import Loader


class Command(ProvisionerCommand):
    help = "Loads IdReg subscription events from SQS"

    def handle(self, *args, **options):
        try:
            Loader().load_subscription_events()
            self.update_job()
        except Exception as err:
            raise CommandError('FAIL: %s' % (err))
