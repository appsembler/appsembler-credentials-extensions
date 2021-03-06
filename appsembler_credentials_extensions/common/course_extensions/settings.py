"""Get common settings from the environment."""

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


ENV_TOKENS = getattr(settings, "ENV_TOKENS", {}).get('APPSEMBLER_FEATURES', {})

# lightweight credits
ENABLE_CREDITS_EXTRA_FIELDS = ENV_TOKENS.get("ENABLE_CREDITS_EXTRA_FIELDS", False)
CREDIT_PROVIDERS = ENV_TOKENS.get("CREDIT_PROVIDERS", [])
CREDIT_PROVIDERS_DEFAULT = ENV_TOKENS.get("CREDIT_PROVIDERS_DEFAULT", None)
DEFAULT_ACCREDITATION_HELP = _("Additional or alternative explanation of accreditation conferred, "
                               "standards met, or similar description.")
ACCREDITATION_CONFERRED_HELP = ENV_TOKENS.get("ACCREDITATION_CONFERRED_HELP", DEFAULT_ACCREDITATION_HELP)

# so far these are just used by NYIF but go on their certs
ENABLE_INSTRUCTION_TYPE_EXTRA_FIELDS = ENV_TOKENS.get("ENABLE_INSTRUCTION_TYPE_EXTRA_FIELDS", [])
COURSE_INSTRUCTIONAL_METHODS = ENV_TOKENS.get("COURSE_INSTRUCTIONAL_METHODS", [])
COURSE_FIELDS_OF_STUDY = ENV_TOKENS.get("COURSE_FIELDS_OF_STUDY", [])
COURSE_INSTRUCTIONAL_METHOD_DEFAULT = ENV_TOKENS.get("COURSE_INSTRUCTIONAL_METHOD_DEFAULT", None)
COURSE_INSTRUCTION_LOCATIONS = ENV_TOKENS.get("COURSE_INSTRUCTION_LOCATIONS", [])
COURSE_INSTRUCTION_LOCATION_DEFAULT = ENV_TOKENS.get("COURSE_INSTRUCTION_LOCATION_DEFAULT", None)
