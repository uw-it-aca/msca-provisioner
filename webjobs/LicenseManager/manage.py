execfile('D:/home/site/wwwroot/env/Scripts/activate_this.py', dict(__file__='D:/home/site/wwwroot/env/Scripts/activate_this.py'))

import os
import django
from django.core.management import call_command

management_command = 'process_subscriptions'

os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "msca_provisioner.settings")

django.setup()
call_command(management_command)
