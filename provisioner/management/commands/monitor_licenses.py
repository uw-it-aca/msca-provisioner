from django.core.management.base import CommandError
from provisioner.management.commands import ProvisionerCommand
from provisioner.monitor import Monitor


class Command(ProvisionerCommand):
    help = "Monitors Office365 for Licenses, updates subscription state"

    def handle(self, *args, **options):
        try:
            monitor = Monitor()
            monitor.confirm_activation();
            monitor.confirm_deactivation();
            self.update_job()
        except Exception as err:
            raise CommandError('FAIL: %s' % (err))
