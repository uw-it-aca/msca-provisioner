"""
Django settings for msca_provisioner project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MSCA_MANAGER_SUPPORT_GROUP = 'u_acadev_msca_support'
MSCA_MANAGER_ADMIN_GROUP = MSCA_MANAGER_SUPPORT_GROUP
RESTCLIENTS_ADMIN_GROUP = MSCA_MANAGER_ADMIN_GROUP
USERSERVICE_ADMIN_GROUP = MSCA_MANAGER_ADMIN_GROUP

AUTHZ_GROUP_BACKEND = 'authz_group.authz_implementation.uw_group_service.UWGroupService'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ['DJANGO_DEBUG'])

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    os.getenv('DJANGO_ALLOWED_HOSTS', '*')
]

SUPPORTTOOLS_PARENT_APP = 'Office 365'
SUPPORTTOOLS_PARENT_APP_URL = 'https://outlook.office.com'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'templatetag_handlebars',
    'supporttools',
    'userservice',
    'authz_group',
    'compressor',
    'restclients',
    'provisioner',
    'events',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'userservice.user.UserServiceMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'supporttools.context_processors.supportools_globals',
    'supporttools.context_processors.has_less_compiled',
)

AUTHENTICATION_BACKENDS = (
     'django.contrib.auth.backends.RemoteUserBackend',
)

#from django_mobileesp.detector import agent
#DETECT_USER_AGENTS = {
#    'is_tablet': agent.detectTierTablet,
#    'is_mobile': agent.detectMobileQuick,
#}

ROOT_URLCONF = 'msca_provisioner.urls'

WSGI_APPLICATION = 'msca_provisioner.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

try:
    DB_DEFAULT = {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': os.environ['DJANGO_DB_NAME'],
        'USER': os.environ['DJANGO_DB_USER'],
        'PASSWORD': os.environ['DJANGO_DB_PASSWORD'],
        'HOST': os.environ['DJANGO_DB_HOST'],
        'PORT': os.environ['DJANGO_DB_PORT'],
        'OPTIONS': {
            'driver': 'SQL Server Native Client 11.0',
        }
    }
except KeyError:
    DB_DEFAULT = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3'
    }


DATABASES = {
    'default': DB_DEFAULT
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Set Static file path
PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static').replace('\\','/')

from socket import gethostname
# Logging
LOG_LEVEL = 'DEBUG'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.getenv('LOGPATH', '.'), 'provisioner-%s.log' % gethostname()),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers':['file'],
            'propagate': False,
            'level': 'INFO'
        },
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level': LOG_LEVEL
        },
        'aws_message': {
            'handlers':['file'],
            'propagate': True,
            'level': LOG_LEVEL
        },
        'provisioner': {
            'handlers': ['file'],
            'level': LOG_LEVEL
        },
        'events': {
            'handlers': ['file'],
            'level': LOG_LEVEL
        },
    }
}


#COMPRESSOR SETTINGS
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

RESTCLIENTS_GWS_DAO_CLASS = 'restclients.dao_implementation.gws.Live'
RESTCLIENTS_GWS_HOST='https://groups.uw.edu'
RESTCLIENTS_GWS_KEY_FILE=os.environ['UWNETID_KEY_FILE']
RESTCLIENTS_GWS_CERT_FILE=os.environ['UWNETID_CERT_FILE']

# UW NetId Web Service settings
RESTCLIENTS_UWNETID_DAO_CLASS = 'restclients.dao_implementation.uwnetid.Live'
RESTCLIENTS_UWNETID_HOST=os.environ['UWNETID_HOST']
RESTCLIENTS_UWNETID_KEY_FILE=os.environ['UWNETID_KEY_FILE']
RESTCLIENTS_UWNETID_CERT_FILE=os.environ['UWNETID_CERT_FILE']


# Office 365 settings
RESTCLIENTS_O365_DAO_CLASS = 'restclients.dao_implementation.o365.Live'
RESTCLIENTS_O365_PRINCIPLE_DOMAIAN=os.environ['O365_PRINCIPLE_DOMAIN']
RESTCLIENTS_O365_TENANT=os.environ['O365_TENANT']
RESTCLIENTS_O365_CLIENT_ID=os.environ['O365_CLIENT_ID']
RESTCLIENTS_O365_CLIENT_SECRET=os.environ['O365_CLIENT_SECRET']


# Dictionary mapping subscription codes to Office 365 licenses.
# Each subscription code is a dictionary of license SKU Part
# Numbers that contain a list of disabled service plans within
# the license.
O365_LICENSES = {
    'O365_TEST_LICENSE_MAP': {
        234: {   # UW Office 365 Education (Dogfood)'
            'STANDARDWOFFPACK_IW_FACULTY': []
            #'STANDARDWOFFPACK_FACULTY': []
        },
        236 : {  # UW Office 365 ProPlus (Dogfood)'
            'OFFICESUBSCRIPTION_FACULTY': []
        },
        238: {   # UW Project Server Online user access (Dogfood)'
            'PROJECTONLINE_PLAN_1_FACULTY': []
        },
        240: {   # UW Power BI (Dogfood)'
            'POWER_BI_STANDARD': []
        }
    },
    'O365_PRODUCTION_LICENSE_MAP': {
        233: {   # UW Office 365 Education'
            'STANDARDWOFFPACK_FACULTY': []
        },
        235: {   # UW Office 365 ProPlus'
            'OFFICESUBSCRIPTION_FACULTY': []
        },
        237: {   # UW Project Server Online user access'
            'PROJECTONLINE_PLAN_1_FACULTY': []
        },
        239: {   # UW Power BI'
            'POWER_BI_STANDARD': []
        }
    }
}

O365_LICENSE_MAP = O365_LICENSES[os.environ['LICENSE_MAP']]

O365_LIMITS = {
    'process' : {
        'default': 250
    },
    'monitor' : {
        'default': 250
    }
}

RESTCLIENTS_CA_BUNDLE = os.environ['CA_BUNDLE']
RESTCLIENTS_TIMEOUT = None
AWS_CA_BUNDLE = os.environ['CA_BUNDLE']

AWS_SQS = {
    'SUBSCRIPTION' : {
        'TOPIC_ARN' : os.environ['SQS_SUBSCRIPTION_TOPIC_ARN'],
        'QUEUE': os.environ['SQS_SUBSCRIPTION_QUEUE'],
        'KEY_ID': os.environ['SQS_SUBSCRIPTION_KEY_ID'],
        'KEY': os.environ['SQS_SUBSCRIPTION_KEY'],
        'VISIBILITY_TIMEOUT': 60,
        'MESSAGE_GATHER_SIZE': 100,
        'VALIDATE_SNS_SIGNATURE': True,
        'VALIDATE_MSG_SIGNATURE': True,
        'EVENT_COUNT_PRUNE_AFTER_DAY': 2,
        'PAYLOAD_SETTINGS': {
            'SUBSCRIPTIONS': O365_LICENSES[os.environ['LICENSE_MAP']]
        }
    }
}

# admin app settings
ADMIN_EVENT_GRAPH_FREQ = 10
ADMIN_SUBSCRIPTION_STATUS_FREQ = 30
