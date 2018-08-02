# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from functools import wraps
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def cms_only(func):
    """ can only be run in CMS context
    """
    @wraps(func)
    def noop_handler(*args, **kwargs):
        logger.warn('{} signal handler disabled since not in CMS context'.format(func.__name__))

    if hasattr(settings, 'STUDIO_NAME'):  # cms (this is more versatile for tests than looking at SERVICE_VARIANT)
        return func
    else:
        noop_handler.__name__ = str('noop_handler_{}'.format(func.__name__))
        return noop_handler


def cms_import_helper():
    # if we are in CMS we need to mock out unimportable modules
    # load a fake certificates.views.support module for now
    class FakeModule(object):
        """I'm fake."""

        __path__ = []

    import sys
    logger.warn("Setting fake certificates.views.support module for CMS.  Not used in Studio")
    sys.modules['lms.djangoapps.certificates.views.support'] = FakeModule()  # load an emtpty module
    sys.modules['certificates.views.support'] = FakeModule()  # load an emtpty module


def disable_if_certs_feature_off(func):
    @wraps(func)
    def noop_func(*args, **kwargs):
        logger.warn('{} disabled since CERTIFICATES_ENABLED is False'.format(func.__name__))

    if settings.FEATURES.get('CERTIFICATES_ENABLED', False):
        return func
    else:
        noop_func.__name__ = str('noop_func_{}'.format(func.__name__))  # py2.7 needs __name__ as String obj
        return noop_func
