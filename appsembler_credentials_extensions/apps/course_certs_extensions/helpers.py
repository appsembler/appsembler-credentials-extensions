# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from functools import wraps
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def disable_if_certs_feature_off(func):
    @wraps(func)
    def noop_func(*args, **kwargs):
        logger.warn('{} disabled since CERTIFICATES_ENABLED is False'.format(func.__name__))

    if settings.FEATURES.get('CERTIFICATES_ENABLED', False):
        return func
    else:
        noop_func.__name__ = str('noop_func_{}'.format(func.__name__))  # py2.7 needs __name__ as String obj
        return noop_func
