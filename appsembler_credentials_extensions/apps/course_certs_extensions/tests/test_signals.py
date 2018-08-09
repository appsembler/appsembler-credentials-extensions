# -*- coding: utf-8 -*-

"""Unit tests for signal handlers on course publication activity."""

from __future__ import absolute_import, unicode_literals

from functools import wraps
import json
import mock
import os

from django.conf import settings

from certificates.models import CertificateGenerationConfiguration
from certificates import api as certs_api
from course_modes.models import CourseMode
from openedx.core.djangoapps.self_paced.models import SelfPacedConfiguration
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from appsembler_credentials_extensions.apps.course_certs_extensions import signals


def certs_feature_enabled(func):
    @wraps(func)
    @mock.patch.dict('appsembler_credentials_extensions.apps.course_certs_extensions.signals.settings.FEATURES', {'CERTIFICATES_HTML_VIEW': True})
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

    @certs_feature_enabled
    def test_default_mode_on_course_pre_publish(self):
        """Verify a CourseMode is created in default mode on course pre-publish.
        """
        DEFAULT_MODE = dict(name='Honor', min_price=0, currency='usd')
        with mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.CourseMode.DEFAULT_MODE', new=DEFAULT_MODE):
            with mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.CourseMode.DEFAULT_MODE_SLUG', new='honor'):
                with self.assertRaises(CourseMode.DoesNotExist):
                    mode = CourseMode.objects.get(course_id=self.course.id, mode_slug='honor', mode_display_name='Honor')

                signals._default_mode_on_course_pre_publish(self.store, self.course.id)
                mode = CourseMode.objects.get(
                    course_id=self.course.id,
                    mode_slug='honor',
                    mode_display_name='Honor'
                )
                self.assertEqual(mode.mode_slug, 'honor')
                self.assertTrue(mode.mode_display_name, 'Honor')


class FakeStaticStorage(object):
    def path(self, asset_path):
        return os.path.join(settings.COMMON_TEST_DATA_ROOT, asset_path)


class CertsCreationSignalsTest(BaseCertSignalsTestCase):
    """ Tests for signal handlers which set up certificates.  None of the handlers should do anything
        if certificates feature is not enabled.
    """


    def fake_get_storage_class(foo):
        return FakeStaticStorage

    @mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.get_storage_class', new=fake_get_storage_class)
    def test_store_theme_signature_img_as_asset(self):
        """ Verify that an file passed as a signature image is stored as a course content asset
        """
        asset_file = "demo-sig1.png"
        signals.store_theme_signature_img_as_asset(self.course.id, asset_file)

    @mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.get_storage_class', new=fake_get_storage_class)
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
                    "signature_image_path": "demo-sig1.png"
                }
            )

            cert_string = signals.make_default_cert(self.course.id)
            cert_dict = json.loads(cert_string)

            self.assertEqual(cert_dict["course_title"], "")
            self.assertEqual(cert_dict["name"], "Default")
            self.assertTrue(cert_dict["is_active"])
            self.assertEqual(cert_dict["version"], 1)
            self.assertFalse(cert_dict["editing"])
            self.assertEqual(cert_dict["description"], "Default certificate")

            signatories = cert_dict["signatories"]
            self.assertTrue(len(signatories), 1)
            self.assertIsInstance(signatories[0], dict)
            self.assertEqual(signatories[0]['name'], 'Name One')
            self.assertEqual(signatories[0]['title'], 'Some Title, Other Title')
            self.assertEqual(signatories[0]['organization'], 'organization')

            self.mock_app_settings.DEFAULT_CERT_SIGNATORIES = [
                {
                    "name": "Ñámè Öñê",
                    "title": "Sømé Tîtlë",
                    "organization": "órg®ñÏzåtïøn",
                    "signature_image_path": "demo-sig1.png"
                },
            ]
            cert_string = signals.make_default_cert(self.course.id)
            cert_dict = json.loads(cert_string)
            signatories = cert_dict["signatories"]
            self.assertEqual(signatories[0]['name'], 'Ñámè Öñê')
            self.assertEqual(signatories[0]['title'], 'Sømé Tîtlë')
            self.assertEqual(signatories[0]['organization'], 'órg®ñÏzåtïøn')

    @mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.get_storage_class', new=fake_get_storage_class)
    @certs_feature_enabled
    def test_make_default_active_cert(self):
        """Verify creation of a default active certificate matching the default cert string."""

        # TODO: can't seem to get self.course.certificates to persist in the store in the tests
        # ... so all this does really is make sure no errors are thrown

        # self.assertEqual(len(self.course.certificates), 0)

        self.mock_app_settings.ACTIVATE_DEFAULT_CERTS = True
        self.mock_app_settings.DEFAULT_CERT_SIGNATORIES = [
            {
                "name": "Ñámè Öñê",
                "title": "Sømé Tîtlë",
                "organization": "órg®ñÏzåtïøn",
                "signature_image_path": "demo-sig1.png"
            },
        ]

        signals._make_default_active_certificate('foo', self.course.id)
        # self.assertEqual(len(self.course.certificates), 0)

        with mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.signals.app_settings.USE_OPEN_ENDED_CERTS_DEFAULTS', new=True):
            signals._make_default_active_certificate('foo', self.course.id)
            # self.assertEqual(len(self.course.certificates), 1)
