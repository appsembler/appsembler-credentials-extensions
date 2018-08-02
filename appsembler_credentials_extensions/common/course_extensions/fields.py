"""Custom field types for mixin class fields."""

from __future__ import absolute_import, print_function, unicode_literals

import traceback

from xblock import warnings
from xblock.fields import Field, String, Scope, UNSET, UNIQUE_ID


class FailingEnforceDefaultValueWarning(DeprecationWarning):
    """
    An exception triggered when a field default value is not among values options.
    """
    pass


class DefaultValueEnforcedField(Field):
    """ Field that enforces a default value among set values."""

    # We're OK redefining built-in `help`
    def __init__(self, help=None, default=UNSET, scope=Scope.content,  # pylint:disable=redefined-builtin
                 display_name=None, values=None, enforce_type=False,
                 xml_node=False, force_export=False, **kwargs):
        self.warned = False
        self.help = help
        self._enable_enforce_type = enforce_type
        self.scope = scope
        self._display_name = display_name
        self._values = values
        if default is not UNSET:
            if default is UNIQUE_ID:
                self._default = UNIQUE_ID
            else:
                type_checked = self._check_or_enforce_type(default)
                self._default = self._enforce_default_value(type_checked)
        self.runtime_options = kwargs
        self.xml_node = xml_node
        self.force_export = force_export

    def _enforce_default_value(self, value):
        """
        Depending on whether enforce_value is enabled call self.enforce_default_value and
        return the result or call it and trigger a silent warning if the result
        is different or a Traceback
        """
        if value is None or self.values is None:
            return value
        elif value not in [val['value'] for val in self.values]:
            message = "The default value {!r} was not among available values {} ({})".format(
                value, str(self.values), traceback.format_exc().splitlines()[-1])
            warnings.warn(message, FailingEnforceDefaultValueWarning, stacklevel=3)
            raise ValueError
        else:
            return value


class DefaultEnforcedString(DefaultValueEnforcedField, String):
    pass
