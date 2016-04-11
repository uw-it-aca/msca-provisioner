from django.db import models


class Subscription(models.Model):
    ACTION_SHOW = "show"
    ACTION_ACTIVATE = "activate"
    ACTION_DEACTIVATE = "deactivate"
    ACTION_MODIFY = "modify"
    ACTION_SETNAME = "setname"
    ACTION_DISUSER = "disuser"
    ACTION_REUSER = "reuser"

    ACTION_CHOICES = (
        (ACTION_SHOW, "Show"),
        (ACTION_ACTIVATE, "Activate"),
        (ACTION_DEACTIVATE, "Deactivate"),
        (ACTION_MODIFY, "Modify"),
        (ACTION_SETNAME, "Setname"),
        (ACTION_DISUSER, "Disuser"),
        (ACTION_REUSER, "Reuser"),
    )

    STATE_INITIAL = "initial"
    STATE_ACTIVE = "active"
    STATE_DELETED = "deleted"
    STATE_PENDING = "pending"
    STATE_FAILED = "failed"
    STATE_DISUSER = "disuser"

    STATE_CHOICES = (
        (STATE_INITIAL, "Initial"),
        (STATE_ACTIVE, "Active"),
        (STATE_DELETED, "Deleted"),
        (STATE_PENDING, "Pending"),
        (STATE_FAILED, "Failed"),
        (STATE_DISUSER, "Disuser"),
    )

    net_id = models.CharField(max_length=20, unique=True)
    subscription = models.SmallIntegerField(default=0)
    state = models.CharField(max_length=16, choices=STATE_CHOICES)


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
