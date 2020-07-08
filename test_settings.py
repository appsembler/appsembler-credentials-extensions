"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from __future__ import absolute_import, unicode_literals

from os import environ
from os.path import abspath, dirname, join

from cms.envs.common import *

# Hawthorn introduces derived settings
try:
    from openedx.core.lib.derived import derive_settings
    derive_settings(__name__)
    DEFAULT_TEMPLATE_ENGINE = TEMPLATES[0]
except ImportError:
    pass

def root(*args):
    """Get the absolute path of the given path relative to the project root."""
    return join(abspath(dirname(__file__)), *args)

PROJECT_ROOT = path(__file__).abspath().dirname()
COMMON_TEST_DATA_ROOT = PROJECT_ROOT / "tests" / "data"

LMS_INTERNAL_ROOT_URL = "localhost"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.{}.db'.format(os.environ.get('EDX_PLATFORM_VERSION', '')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

MONGO_PORT_NUM = int(os.environ.get('EDXAPP_TEST_MONGO_PORT', '27017'))
MONGO_HOST = os.environ.get('EDXAPP_TEST_MONGO_HOST', 'localhost')

CONTENTSTORE = {
    'ENGINE': 'xmodule.contentstore.mongo.MongoContentStore',
    'DOC_STORE_CONFIG': {
        'host': MONGO_HOST,
        'db': 'test_xcontent',
        'port': MONGO_PORT_NUM,
        'collection': 'dont_trip',
    },
    # allow for additional options that can be keyed on a name, e.g. 'trashcan'
    'ADDITIONAL_OPTIONS': {
        'trashcan': {
            'bucket': 'trash_fs'
        }
    }
}

test_apps = (
    'certificates',  # needed for some test setup
    'badges',  # needed for some test setup
    'appsembler_credentials_extensions.apps.course_certs_extensions.apps.AppsemblerCredentialsCourseCertsConfig',
    'appsembler_credentials_extensions.apps.badges_extensions.apps.AppsemblerCredentialsBadgesConfig',
)

try:
    INSTALLED_APPS = INSTALLED_APPS + test_apps
except TypeError:
    INSTALLED_APPS = INSTALLED_APPS + list(test_apps)  # Hawthorn+

LOCALE_PATHS = [
    root('appsembler_credentials_extensions', 'conf', 'locale'),
]

# ROOT_URLCONF = 'appsembler_credentials_extensions.urls'

SECRET_KEY = 'insecure-secret-key'
