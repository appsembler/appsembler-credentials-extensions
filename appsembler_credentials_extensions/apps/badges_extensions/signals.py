# -*- coding: utf-8 -*-
"""Custom signal handlers for badges."""

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.dispatch.dispatcher import receiver

from xmodule.modulestore.django import SignalHandler, modulestore

from appsembler_credentials_extensions.apps.badges_extensions import app_settings


@receiver(SignalHandler.pre_publish)
def _change_badges_setting_on_pre_publish(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    """Turn off issue_badges on a course.

    We do this if feature not enabled, or we explicitly disable course
    completion badges. At present, course completion badges don't work properly
    with Badgr so we use course group badging and have to turn off
    `issue_badges`.
    """

    store = modulestore()
    course = store.get_course(course_key)
    use_badges = settings.FEATURES.get('ENABLE_OPENBADGES', False)
    if not use_badges or app_settings.DISABLE_COURSE_COMPLETION_BADGES:
        course.issue_badges = False
    course.save()
    try:
        store.update_item(course, course._edited_by)
    except AttributeError:
        store.update_item(course, 0)
