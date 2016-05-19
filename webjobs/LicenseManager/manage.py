execfile('D:/home/site/wwwroot/env/Scripts/activate_this.py', dict(__file__='D:/home/site/wwwroot/env/Scripts/activate_this.py'))

import sys

package_paths = [
    r'D:\home\site\wwwroot\env\Lib\site-packages',
    r'D:\home\site\wwwroot'
]

for path in package_paths:
    sys.path.append(path)

import os
import django
from django.core.management import call_command

os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "msca_provisioner.settings")

django.setup()
call_command('process_subscriptions')
