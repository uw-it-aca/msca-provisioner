from django.db import models


class SubscriptionLog(models.Model):
    """ Record Event Frequency
    """
    minute = models.IntegerField(default=0)
    event_count = models.SmallIntegerField(default=0)

