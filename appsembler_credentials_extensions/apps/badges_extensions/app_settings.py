"""Get app settings from the environment."""

from __future__ import absolute_import, unicode_literals

from django.conf import settings


ENV_TOKENS = getattr(settings, "ENV_TOKENS", {}).get('APPSEMBLER_FEATURES', {})

# badges
DISABLE_COURSE_COMPLETION_BADGES = ENV_TOKENS.get("DISABLE_COURSE_COMPLETION_BADGES", False)
