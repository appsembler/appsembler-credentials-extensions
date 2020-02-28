# -*- coding: utf-8 -*-
"""Monkeypatches on course certificate behavior."""

from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings

# both are in sys.modules and need to be monkeypatched
from lms.djangoapps.certificates.signals import toggle_self_generated_certs as toggle_self_generated_certs_fullpath
from certificates.signals import toggle_self_generated_certs

from appsembler_credentials_extensions.common.course_extensions.mixins import get_CourseDescriptor_mixins


logger = logging.getLogger(__name__)

if hasattr(settings, 'STUDIO_NAME'):  # cms
    from .helpers import cms_import_helper
    cms_import_helper()


def _update_course_context(request, context, course, platform_name):
    """Course-related context for certificate webview, extended with Mixin fields."""
    orig__update_course_context(request, context, course, platform_name)

    # add our course extension fields
    course_mixins = get_CourseDescriptor_mixins()
    for mixin in course_mixins:
        for f in mixin.fields:
            context[f] = getattr(course, f)


if not hasattr(settings, 'STUDIO_NAME'):  # only do this in LMS
    logger.warn('Monkeypatching lms.djangoapps.certificates.views.webview._update_course_context '
                'to extend with Appsembler Mixin fields')
    from lms.djangoapps.certificates.views import webview
    orig__update_course_context = webview._update_course_context
    webview._update_course_context = _update_course_context

# replace certificates handler which always enables self-gen'd certs for self-paced courses
# with ours that only enables self-gen'd certs on self-paced if we set feature flag for it
# we have to disable celery tasks already registered for signal handlers in edx-platform
logger.warn('Monkeypatching lms.djangoapps.certificates.signals.toggle_self_generated_certs to '
            'limit enabling of self-generated certs on self-paced courses by feature flag.')
orig_toggle_self_generated_certs = toggle_self_generated_certs
orig_toggle_self_generated_certs_fullpath = toggle_self_generated_certs_fullpath
orig_toggle_self_generated_certs.delay = lambda course_key, enable: None
orig_toggle_self_generated_certs_fullpath.delay = lambda course_key, enable: None
