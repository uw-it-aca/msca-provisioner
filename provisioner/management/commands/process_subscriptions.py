from django.core.management.base import CommandError
from provisioner.management.commands import ProvisionerCommand
from provisioner.license import License


class Command(ProvisionerCommand):
    help = "Initiates Office365 Licensing from Subscriptions"

    def handle(self, *args, **options):
        try:
            License().process()
            self.update_job()
        except Exception as err:
            raise CommandError('FAIL: %s' % (err))
