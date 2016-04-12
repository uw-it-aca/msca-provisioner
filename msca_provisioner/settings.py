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


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    os.environ['DJANGO_ALLOWED_HOSTS']
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
    'supporttools',
    'userservice',
    'compressor',
    'provisioner',
    'events',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'userservice.user.UserServiceMiddleware',
    'django_mobileesp.middleware.UserAgentDetectionMiddleware',
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

from django_mobileesp.detector import agent
DETECT_USER_AGENTS = {
    'is_tablet': agent.detectTierTablet,
    'is_mobile': agent.detectMobileQuick,
}

ROOT_URLCONF = 'msca_provisioner.urls'

WSGI_APPLICATION = 'msca_provisioner.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
print 'HOST HOST HOST %s' % (os.environ['DJANGO_DB_HOST'])
DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': os.environ['DJANGO_DB_NAME'],
        'USER': os.environ['DJANGO_DB_USER'],
        'PASSWORD': os.environ['DJANGO_DB_PASSWORD'],
        'HOST': os.environ['DJANGO_DB_HOST'],
        'PORT': os.environ['DJANGO_DB_PORT'],
        'OPTIONS': {
            'driver': 'SQL Server Native Client 11.0',
        },
    }
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
            'level':'INFO',
        },
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'provisioner': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'events': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}


#COMPRESSOR SETTINGS
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False


# KWS settings
RESTCLIENTS_KWS_CERT_FILE=os.environ['KWS_CERT_FILE'],
RESTCLIENTS_KWS_KEY_FILE=os.environ['KWS_KEY_FILE'],
RESTCLIENTS_KWS_HOST = 'https://wseval.s.uw.edu:443'


AWS_SQS = {
    'SUBSCRIPTION' : {
        'TOPIC_ARN' : os.environ['SQS_SUBSCRIPTION_TOPIC_ARN'],
        'QUEUE': os.environ['SQS_SUBSCRIPTION_QUEUE'],
        'KEY_ID': os.environ['SQS_SUBSCRIPTION_KEY_ID'],
        'KEY': os.environ['SQS_SUBSCRIPTION_KEY'],
        'VISIBILITY_TIMEOUT': 60,
        'MESSAGE_GATHER_SIZE': 12,
        'VALIDATE_SNS_SIGNATURE': True,
        'VALIDATE_MSG_SIGNATURE': True,
        'EVENT_COUNT_PRUNE_AFTER_DAY': 2,
        'PAYLOAD_SETTINGS': {}
    },
}
