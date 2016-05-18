import sys
import os
import django
from django.core.management import call_command

management_command = 'process_subscriptions'

package_paths = [
    r'D:\home\site\wwwroot\env\Lib\site-packages',
    r'D:\home\site\wwwroot'
]

for path in package_paths:
    sys.path.append(path)

os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "msca_provisioner.settings")

django.setup()
call_command(management_command)
