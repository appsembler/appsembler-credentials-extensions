# -*- coding: utf-8 -*-
"""Tests for course_extensions mixins."""

from __future__ import absolute_import, unicode_literals

import importlib
import mock

from django.conf import settings

from xblock.fields import Scope, String, XBlockMixin
from xmodule import course_module
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from .. import mixins, fields


TEST_CREDIT_PROVIDERS = [
    'Proviseur de crédit',
    'Credit Provider'
]

TEST_CREDIT_PROVIDER_DEFAULT = 'foo'


class CourseMixinsTestCase(ModuleStoreTestCase):
    """ Tests for monkeypatches in course_certs_extensions app."""

    def setUp(self):
        super(CourseMixinsTestCase, self).setUp()

    def test_get_CourseDescriptor_mixins(self):
        """ Verify proper mixin classes are returned based on settings."""
        extra_classes = mixins.get_CourseDescriptor_mixins()
        self.assertIn(mixins.XMLDefinitionChainingMixin, extra_classes)
        self.assertNotIn(mixins.CreditsMixin, extra_classes)
        self.assertNotIn(mixins.InstructionTypeMixin, extra_classes)

        with mock.patch('appsembler_credentials_extensions.common.course_extensions.settings.ENABLE_CREDITS_EXTRA_FIELDS', new=True):
            extra_classes = mixins.get_CourseDescriptor_mixins()
            self.assertIn(mixins.CreditsMixin, extra_classes)

        with mock.patch('appsembler_credentials_extensions.common.course_extensions.settings.ENABLE_INSTRUCTION_TYPE_EXTRA_FIELDS', new=True):
            extra_classes = mixins.get_CourseDescriptor_mixins()
            self.assertIn(mixins.InstructionTypeMixin, extra_classes)

    def test_credits_mixin_fields(self):
        """ Verify proper fields are added, field values are correct."""

        # TODO: is there a better way to do this instead of forcing the update to _values here? can't seem to reload() the module
        # and class fields and get new values from mocked TEST_CREDIT_PROVIDERS
        mixins.CreditsMixin.credit_provider._values = mixins.build_field_values(TEST_CREDIT_PROVIDERS)
        course = CourseFactory.create()
        course.__class__ = type(str('CourseDescriptorWithCredits'), (course_module.CourseDescriptor, mixins.CreditsMixin), {})
        field_keys = course.fields.keys()
        self.assertIn('credit_provider', field_keys)
        self.assertIn('credits', field_keys)
        self.assertIn('credit_unit', field_keys)
        self.assertIn('accreditation_conferred', field_keys)

        self.assertEqual([
            {'value': 'Proviseur de crédit', 'display_name': 'Proviseur de crédit'},
            {'value': 'Credit Provider', 'display_name': 'Credit Provider'},
        ], course.__class__.fields['credit_provider'].values)

        # can't set a default that's not in the CREDIT_PROVIDERS values
        with self.assertRaises(ValueError):
            new_provider_field = fields.DefaultEnforcedString(
                values=mixins.build_field_values(TEST_CREDIT_PROVIDERS),
                default=TEST_CREDIT_PROVIDER_DEFAULT
            )
