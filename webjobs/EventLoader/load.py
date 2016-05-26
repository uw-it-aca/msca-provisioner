execfile('D:/home/site/wwwroot/env/Scripts/activate_this.py', dict(__file__='D:/home/site/wwwroot/env/Scripts/activate_this.py'))

import sys

package_paths = [
    r'D:\home\site\wwwroot\env\Lib\site-packages',
    r'D:\home\site\wwwroot'
]

for path in package_paths:
    sys.path.append(path)

import os
import time
import django
from django.core.management import call_command
from logging import getLogger

os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "msca_provisioner.settings")

django.setup()
log = getLogger('provisioner')
while True:
    in_time = int(time.time())
    log.debug('calling load_subsciptions')
    call_command('load_subscriptions')

    run_time = int(time.time()) - in_time
    if run_time < 3:
        log.debug("Quick run: pause 15")
        time.sleep(15)
    elif run_time < 10:
        log.debug("Long run: pause 5")
        time.sleep(10)
    else:
        log.debug("Ran %s seconds: no pause" % (run_time))
