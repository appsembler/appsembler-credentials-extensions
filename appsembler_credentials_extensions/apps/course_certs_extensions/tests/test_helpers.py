"""Test misc. helper methods in course_certs_extensions."""


from __future__ import absolute_import, unicode_literals

import mock

from django.test import TestCase

from .. import helpers


class CertsHelpersTestCase(TestCase):
    """ Tests for monkeypatches in course_certs_extensions app."""

    @mock.patch('appsembler_credentials_extensions.apps.course_certs_extensions.helpers.settings', new=object())
    def test_disable_when_certs_feature_off(self):
        """ Test disabling a function when the Open edX certificates feature is turned off."""

        mock_decorated = mock.Mock()
        mock_decorated.__name__ = str('mocked')  # needed for functools.wrap
        ret_func = helpers.cms_only(mock_decorated)
        self.assertNotEqual(ret_func, mock_decorated)
        self.assertTrue('noop_handler' in ret_func.__name__)

    @mock.patch.dict('appsembler_credentials_extensions.apps.course_certs_extensions.helpers.settings.FEATURES', {'CERTIFICATES_ENABLED': False})
    def test_signal_handlers_disabler_decorator(self):
        """ Verify decorator works to return a noop function if CERTIFICATES_ENABLED is False
        """
        mock_decorated = mock.Mock()
        mock_decorated.__name__ = str('mocked')  # needed for functools.wrap
        ret_func = helpers.disable_if_certs_feature_off(mock_decorated)
        self.assertNotEqual(ret_func, mock_decorated)
        self.assertTrue('noop_func' in ret_func.__name__)
