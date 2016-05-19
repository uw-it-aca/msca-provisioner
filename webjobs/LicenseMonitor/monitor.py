execfile('D:/home/site/wwwroot/env/Scripts/activate_this.py', dict(file='D:/home/site/wwwroot/env/Scripts/activate_this.py'))

import os
import django
from django.core.management import call_command

management_command = 'monitor_licenses'

os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "msca_provisioner.settings")

django.setup()
call_command(management_command)
