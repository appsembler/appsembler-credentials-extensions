# -*- coding: utf-8 -*-

"""appsembler_credentials_extensions.course_certs_extensions Django application initialization."""

from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class AppsemblerCredentialsCourseCertsConfig(AppConfig):
    """Configuration for the appsembler_course_certs_extensions Django application."""

    name = 'appsembler_credentials_extensions.apps.course_certs_extensions'
    label = 'appsembler_course_certs_extensions'
    verbose_name = 'Appsembler Course Certificates Extensions'

    def ready(self):
        """Do stuff after app is ready."""
        from . import monkeypatch  # no-qa
        from . import signals  # no-qa
