# -*- coding: utf-8 -*-

"""appsembler_credentials_extensions.course_certs_extensions Django application initialization."""

from __future__ import absolute_import, unicode_literals

import os

from django.apps import AppConfig
from django.conf import settings


class AppsemblerCredentialsCourseCertsConfig(AppConfig):
    """Configuration for the appsembler_course_certs_extensions Django application."""

    name = 'appsembler_credentials_extensions.apps.course_certs_extensions'
    label = 'appsembler_course_certs_extensions'
    verbose_name = 'Appsembler Course Certificates Extensions'

    def ready(self):
        """Do stuff after app is ready."""
        from . import monkeypatch  # no-qa
        from . import signals  # no-qa

        # disable migrations outside of LMS environment
        if os.environ.get('SERVICE_VARIANT', '').lower() != 'lms':
            # starting Django 1.9 can just set this to `None`
            settings.MIGRATION_MODULES.update({
                'appsembler_course_certs_extensions': "nomigrations"
            })
