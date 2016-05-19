execfile('D:/home/site/wwwroot/env/Scripts/activate_this.py', dict(__file__='D:/home/site/wwwroot/env/Scripts/activate_this.py'))

import os
import time
import django
from django.core.management import call_command

management_command = 'load_subscriptions'

os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "msca_provisioner.settings")

django.setup()
while True:
    in_time = int(time.time())

    call_command(management_command)

    run_time = int(time.time()) - in_time
    if run_time < 3:
        print "Quick run: pause 15"
        time.sleep(15)
    elif run_time < 10:
        print "Long run: pause 5"
        time.sleep(10)
    else:
        print "Ran %s seconds: no pause" % (run_time)
