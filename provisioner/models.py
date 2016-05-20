from django.db import models
from django.utils.timezone import utc, localtime


class Subscription(models.Model):
    STATE_ACTIVATE = "activate"
    STATE_ACTIVATING = "activating"
    STATE_ACTIVE = "active"
    STATE_DELETE = "delete"
    STATE_DELETING = "deleting"
    STATE_DELETED = "deleted"
    STATE_PENDING = "pending"
    STATE_FAILED = "failed"
    STATE_DISUSER = "disuser"

    STATE_CHOICES = (
        (STATE_ACTIVATE, "Activate"),
        (STATE_ACTIVATING, "Activating"),
        (STATE_ACTIVE, "Active"),
        (STATE_DELETE, "Delete"),
        (STATE_DELETING, "Deleting"),
        (STATE_DELETED, "Deleted"),
        (STATE_PENDING, "Pending"),
        (STATE_FAILED, "Failed"),
        (STATE_DISUSER, "Disuser"),
    )

    net_id = models.CharField(max_length=20, unique=True)
    subscription = models.SmallIntegerField(default=0)
    state = models.CharField(max_length=16, choices=STATE_CHOICES)
    modified_date = models.DateTimeField(auto_now=True)
    in_process = models.NullBooleanField()

    def json_data(self):
        return {
            'subscription_id': self.pk,
            'net_id': self.net_id,
            'subscription': self.subscription,
            'state': self.state,
            'modified_date': localtime(self.modified_date).isoformat() if (
                self.modified_date is not None) else None,
            'in_process': self.in_process
        }


class SubscriptionCode(models.Model):
    code = models.SmallIntegerField(default=0)
    name = models.CharField(max_length=128)


class Job(models.Model):
    """ Represents provisioning commands.
    """
    name = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    changed_by = models.CharField(max_length=32)
    changed_date = models.DateTimeField()
    last_run_date = models.DateTimeField(null=True)
    is_active = models.NullBooleanField()

    def json_data(self):
        return {
            'job_id': self.pk,
            'name': self.name,
            'title': self.title,
            'changed_by': self.changed_by,
            'changed_date': localtime(self.changed_date).isoformat() if (
                self.changed_date is not None) else None,
            'last_run_date': localtime(self.last_run_date).isoformat() if (
                self.last_run_date is not None) else None,
            'is_active': self.is_active,
        }
