"""Unit tests for signal handlers on course publication activity."""

from __future__ import absolute_import, unicode_literals

import mock

from django.conf import settings
from django.test.client import RequestFactory

from xblock.fields import Scope, String, XBlockMixin
from xmodule import course_module
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

if hasattr(settings, 'STUDIO_NAME'):  # cms
    from ..helpers import cms_import_helper
    cms_import_helper()

from lms.djangoapps.certificates.views import webview

from .. import monkeypatch


class FakeExtensionMixin(XBlockMixin):
    fake_field = String(default='foo', scope=Scope.settings,)


def mock_get_mixins():
    return (FakeExtensionMixin, )


@mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.monkeypatch.get_CourseDescriptor_mixins',
            new=mock_get_mixins)
class CertsMonkeypatchTestCase(ModuleStoreTestCase):
    """ Tests for monkeypatches in course_certs_extensions app."""

    def setUp(self):
        super(CertsMonkeypatchTestCase, self).setUp()
        # provide the custom mixin class.  that behavior is tested in course_extensions tests
        cd_bases = course_module.CourseDescriptor.__bases__
        course_module.CourseDescriptor.__bases__ = mock_get_mixins() + cd_bases
        self.course = CourseFactory.create()

    def test_certs_webview_context_patch(self):
        """ Verify certificates.views.webview.update_course_context is monkeypatched correctly.
        It should get fields from course mixin classes."""
        context = {'certificate_data': {}, 'organization_long_name': '', 'organization_short_name': ''}
        request = RequestFactory().get('dummy')
        webview._update_course_context(request, context, self.course, "platform name")
        self.assertTrue(context['fake_field'] == 'foo')  # context updated with course's new mixin field's value
