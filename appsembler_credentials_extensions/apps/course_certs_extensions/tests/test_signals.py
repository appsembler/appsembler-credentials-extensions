"""Unit tests for signal handlers on course publication activity."""

from __future__ import absolute_import, unicode_literals

from functools import wraps
import json
import logging
import mock
import os
import unittest

# from django.test import TestCase

from certificates.models import (
    CertificateGenerationConfiguration, CertificateGenerationCourseSetting)
from certificates import api as certs_api
from openedx.core.djangoapps.self_paced.models import SelfPacedConfiguration
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from appsembler_credentials_extensions.apps.course_certs_extensions import signals


logger = logging.getLogger(__name__)


def certs_feature_enabled(func):
    @wraps(func)
    @mock.patch.dict('appsembler_credentials_extensions.apps.course_certs_extensions.signals.settings.FEATURES', {'CERTIFICATES_ENABLED': True})
    def with_certs_enabled(*args, **kwargs):
        # reload to re-evaluate the decorated methods with new setting
        reload(signals)
        return func(*args, **kwargs)

    return with_certs_enabled


class BaseCertSignalsTestCase(ModuleStoreTestCase):

    def setUp(self):
        super(BaseCertSignalsTestCase, self).setUp()
        # allow self-paced courses
        SelfPacedConfiguration(enabled=True).save()
        self.course = CourseFactory.create(self_paced=True)
        self.store = modulestore()
        self.mock_app_settings = mock.Mock()


class LMSCertSignalsTestCase(BaseCertSignalsTestCase):

    def setUp(self):
        super(LMSCertSignalsTestCase, self).setUp()
        # Enable certificates generation config in db, overall
        CertificateGenerationConfiguration.objects.create(enabled=True)


class CertsSettingsSignalsTest(LMSCertSignalsTestCase):
    """ Tests for signal handlers changing cert-related settings on course
        publish or pre-publish.  Some of the handlers should not do anything 
        if certificates feature is not enabled.
    """

    @mock.patch.dict('appsembler_credentials_extensions.apps.course_certs_extensions.signals.settings.FEATURES', {'CERTIFICATES_ENABLED': False})
    def test_signal_handlers_disabler_decorator(self):
        """ Verify decorator works to return a noop function if CERTIFICATES_ENABLED is False
        """
        mock_decorated = mock.Mock()
        mock_decorated.__name__ = str('mocked')  # needed for functools.wrap
        ret_func = signals.disable_if_certs_feature_off(mock_decorated)
        self.assertNotEqual(ret_func, mock_decorated)
        self.assertTrue('noop_handler' in ret_func.__name__)

    @certs_feature_enabled
    def test_cert_related_advanced_settings_as_expected_by_default(self):
        """ Verify that cert-related advanced course settings are what
            we think by default
        """
        self.assertEqual(self.course.certificates_display_behavior, 'end')
        self.assertFalse(self.course.certificates_show_before_end)
        self.assertFalse(self.course.cert_html_view_enabled)

    @certs_feature_enabled
    def test_cert_related_advanced_settings_features(self):
        """ Verify changes to cert-related advanced settings if we
            enable the feature or don't enable it
        """
        signals._change_cert_defaults_on_pre_publish('store', self.course.id)
        course = self.store.get_course(self.course.id)
        self.assertEqual(course.certificates_display_behavior, 'end')
        self.assertFalse(course.certificates_show_before_end)
        self.assertFalse(course.cert_html_view_enabled)

        self.mock_app_settings.USE_OPEN_ENDED_CERTS_DEFAULTS = True
        with mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.app_settings', new=self.mock_app_settings):
            signals._change_cert_defaults_on_pre_publish('store', self.course.id)
            course = self.store.get_course(self.course.id)
            self.assertEqual(course.certificates_display_behavior, 'early_with_info')
            self.assertTrue(course.certificates_show_before_end)
            self.assertTrue(course.cert_html_view_enabled)

    @certs_feature_enabled
    def test_enable_self_generated_certs_on_publish_for_self_paced(self):
        """ Verify the default behavior is maintained, self-generated certs enabled
            for self-paced courses
        """
        self.assertFalse(certs_api.cert_generation_enabled(self.course.id))
        signals.toggle_self_generated_certs(self.course.id, self.course.self_paced)
        self.assertTrue(certs_api.cert_generation_enabled(self.course.id))

    @certs_feature_enabled
    def test_dont_enable_self_generated_certs_on_publish_for_self_paced_when_disabled_by_setting(self):
        """ Verify that self-generated certs are not enabled for self-paced courses
            if it is explicitly disabled by setting
        """
        self.mock_app_settings.DISABLE_SELF_GENERATED_CERTS_FOR_SELF_PACED = True
        with mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.app_settings', new=self.mock_app_settings):
            signals.toggle_self_generated_certs(self.course.id, self.course.self_paced)
            self.assertFalse(certs_api.cert_generation_enabled(self.course.id))

    @certs_feature_enabled
    def test_dont_enable_self_generated_certs_on_publish_for_instructor_paced(self):
        """ Verify that self-generated certs are not enabled for instructor-paced courses
            unless explicitly enabled by setting
        """
        course = CourseFactory.create(self_paced=False)
        self.assertFalse(certs_api.cert_generation_enabled(course.id))
        signals.toggle_self_generated_certs(course.id, course.self_paced)
        self.assertFalse(certs_api.cert_generation_enabled(course.id))

    @certs_feature_enabled
    def test_enable_self_generated_certs_on_publish_for_instructor_paced_if_always_enabled_by_setting(self):
        """ Verify that self-generated certs are enabled for self-paced courses
            if it is explicitly enabled by setting
        """
        self.mock_app_settings.ALWAYS_ENABLE_SELF_GENERATED_CERTS = True
        with mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.app_settings', new=self.mock_app_settings):
            course = CourseFactory.create(self_paced=False)
            signals.toggle_self_generated_certs(course.id, course.self_paced)
            self.assertTrue(certs_api.cert_generation_enabled(course.id))


@unittest.skipUnless(os.environ.get('SERVICE_VARIANT', None) == 'cms', 'only runs in CMS test context')
class CertsCreationSignalsTest(BaseCertSignalsTestCase):
    """ Tests for signal handlers which set up certificates.  None of the handlers should do anything
        if certificates feature is not enabled.
    """

    def test_store_theme_signature_img_as_asset(self):
        """ Verify that an file passed as a signature image is stored as a course content asset
        """
        # this image exists on the filesystem from certificates app static files
        path = "/static/certificates/images/demo-sig1.png"
        signals.store_theme_signature_img_as_asset(self.course.id, path)

    def test_make_default_cert_string(self):
        """ Verify helper function generates a string for default certificate creation
            that can be deserialized to a dictionary with proper values
        """
        from contentstore.views.certificates import CertificateValidationError

        self.mock_app_settings.DEFAULT_CERT_SIGNATORIES = {}
        self.mock_app_settings.ACTIVATE_DEFAULT_CERTS = True
        with mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.app_settings', new=self.mock_app_settings):
            cert_string = signals.make_default_cert(self.course.id)
            cert_dict = json.loads(cert_string)
            self.assertEqual(cert_dict["course_title"], "")
            self.assertEqual(cert_dict["name"], "Default")
            self.assertTrue(cert_dict["is_active"])
            self.assertEqual(cert_dict["signatories"], [])
            self.assertEqual(cert_dict["version"], 1)
            self.assertFalse(cert_dict["editing"])
            self.assertEqual(cert_dict["description"], "Default certificate")

            self.mock_app_settings.DEFAULT_CERT_SIGNATORIES = [
                {
                    "name": "Name One",
                    "title": "Some Title, Other Title",
                    "organization": "organization",
                },
            ]

            # must fail with signatory unless there is a signature path value
            self.assertRaises(CertificateValidationError, signals.make_default_cert, **{"course_key": self.course.id})

            # test an image can be stored
            self.mock_app_settings.DEFAULT_CERT_SIGNATORIES[0].update(
                {
                    "signature_image_path": "/fake/theme/dir/signature_image.jpg"
                }
            )
            # cert_string = signals.make_default_cert(self.course.id)
            # cert_dict = json.loads(cert_string)

            # self.assertEqual(cert_dict["course_title"], "")
            # self.assertEqual(cert_dict["name"], "Default")
            # self.assertTrue(cert_dict["is_active"])
            # self.assertEqual(cert_dict["version"], 1)
            # self.assertFalse(cert_dict["editing"])
            # self.assertEqual(cert_dict["description"], "Default certificate")

            # edge cases: non-ASCII, others...
            # signatories = cert_dict["signatories"]
            # self.assertTrue(len(signatories), 1)
            # self.assertInstance(signatories[0], dict))
            # self.assertEqual(signatories[0]['name'], 'Name One')
            # self.assertEqual(signatories[0]['title'], 'Some Title, Other Title')
            # self.assertEqual(signatories[0]['organization'], 'organization')
