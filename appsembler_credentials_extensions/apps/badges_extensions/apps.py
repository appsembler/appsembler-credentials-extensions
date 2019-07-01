# -*- coding: utf-8 -*-

"""appsembler_credentials_extensions.badges_extensions Django application initialization."""

from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class AppsemblerCredentialsBadgesConfig(AppConfig):
    """Configuration for the appsembler_badges_extensions Django application."""

    name = 'appsembler_credentials_extensions.apps.badges_extensions'
    label = 'appsembler_badges_extensions'
    verbose_name = 'Appsembler Badges Extensions'

    def ready(self):
        """Do stuff after app is ready."""
        from . import signals  # noqa: F401
