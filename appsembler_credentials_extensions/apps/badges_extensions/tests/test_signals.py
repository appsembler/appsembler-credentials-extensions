"""Unit tests for signal handlers on course publication activity."""

from __future__ import absolute_import, unicode_literals

from functools import wraps
import logging
import mock

from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from appsembler_credentials_extensions.apps.badges_extensions import signals


logger = logging.getLogger(__name__)


def badges_feature_enabled(func):
    @wraps(func)
    @mock.patch.dict('appsembler_credentials_extensions.apps.badges_extensions.signals.settings.FEATURES', {'ENABLE_OPENBADGES': True})
    def with_badges_enabled(*args, **kwargs):
        # reload to re-evaluate the decorated methods with new setting
        reload(signals)
        return func(*args, **kwargs)

    return with_badges_enabled


class BadgeSignalsTestCase(ModuleStoreTestCase):
    """ Tests for signal handlers changing badge-related settings on course
        publish or pre-publish.  Some of the handlers should not do anything
        if certificates feature is not enabled.
    """

    def setUp(self):
        super(BadgeSignalsTestCase, self).setUp()
        self.course = CourseFactory.create(self_paced=True)
        self.store = modulestore()
        self.mock_app_settings = mock.Mock()

    def test_badges_remain_disabled_after_pre_publish_with_feature_off(self):
        """ Verify that badges-related advanced course settings are not changed
            when we use related feature settings
        """
        signals._change_badges_setting_on_pre_publish('store', self.course.id)
        course = self.store.get_course(self.course.id)
        self.assertFalse(course.issue_badges)

    @badges_feature_enabled
    def test_badges_remain_disabled_after_pre_publish_with_feature_on_but_course_completion_badges_off(self):
        """ Make sure we can enable to open badges feature overall but keep course completion
            badges off using our setting
        """
        self.mock_app_settings.DISABLE_COURSE_COMPLETION_BADGES = True
        with mock.patch('appsembler_credentials_extensions.apps.badges_extensions.signals.app_settings', new=self.mock_app_settings):
            signals._change_badges_setting_on_pre_publish('store', self.course.id)
            course = self.store.get_course(self.course.id)
            self.assertFalse(course.issue_badges)
