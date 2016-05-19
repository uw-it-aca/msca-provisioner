from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import utc
from provisioner.models import Job
import datetime


class ProvisionerCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(ProvisionerCommand, self).__init__(*args, **kwargs)

        if not self.is_active_job():
            self.handle = self.not_handled

    def not_handled(self, *args, **options):
        return

    def is_active_job(self):
        name = self.name_from_module()
        try:
            job = Job.objects.get(name=name)
        except Job.DoesNotExist:
            job = Job(name=name,
                      title=self.title_from_name(name),
                      is_active=False)
            job.changed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
            job.save()

        return True if job.is_active else False

    def update_job(self):
        job = Job.objects.get(name=self.name_from_module())
        job.last_run_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        job.save()

    def name_from_module(self):
        name = self.__module__.split('.')[-1]
        return name

    def title_from_name(self, name):
        parts = name.split(':')
        title = ' '.join(w.capitalize() for w in parts[0].split('_'))
        args = parts[1:]
        if len(args):
            title += ' (' + ', '.join(args) + ')'
        return title
