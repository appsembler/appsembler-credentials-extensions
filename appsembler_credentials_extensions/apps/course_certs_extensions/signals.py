# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import copy
from functools import partial
import json
import logging

from celery.task import task
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.dispatch.dispatcher import receiver

try:
    from openedx.core.djangoapps.contentserver.caching import del_cached_content
except ImportError:
    from contentserver.caching import del_cached_content
try:
    from contentstore.views import certificates as store_certificates
except ImportError:
    try:
        from cms.djangoapps.contentstore.views import certificates as store_certificates
    except ImportError:
        pass  # some of the other imports in certificates will fail in LMS context but they aren't needed


# don't import from lms.djangoapps.certificates here or it will
# mess up app registration
from lms.djangoapps.certificates.models import CertificateGenerationCourseSetting
from course_modes.models import CourseMode
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.content.course_overviews.signals import COURSE_PACING_CHANGED
from xmodule.contentstore.django import contentstore
from xmodule.contentstore.content import StaticContent
from xmodule.modulestore.django import SignalHandler, modulestore

from . import app_settings
from . import helpers


DEFAULT_CERT = """
    {{"course_title": "", "name": "Default", "is_active": {},
    "signatories": {}, "version": 1, "editing": false,
    "description": "Default certificate"}}
"""


logger = logging.getLogger(__name__)


# TODO: refactor these handlers for DRY


def make_default_cert(course_key):
    """
    Add any signatories to default cert string and return the string
    """

    default_cert = DEFAULT_CERT

    if app_settings.DEFAULT_CERT_SIGNATORIES:
        signatories = app_settings.DEFAULT_CERT_SIGNATORIES

        # use org-specific signatories if defined for this course's org
        if 'course_org_overrides' in signatories:
            try:
                signatories = signatories['course_org_overrides'][course_key.org]
            except (KeyError, TypeError):
                pass
        else:
            try:
                signatories = signatories['default']
            except (KeyError, TypeError):
                pass  # some older configs won't have that key

        updated = []
        for i, sig in enumerate(signatories):
            default_cert_signatory = copy.deepcopy(sig)
            default_cert_signatory['id'] = i
            if default_cert_signatory.get('organization') is None:
                default_cert_signatory.update({'organization': ''})
            try:
                theme_asset_path = sig['signature_image_path']
                sig_img_path = store_theme_signature_img_as_asset(course_key, theme_asset_path)
                default_cert_signatory['signature_image_path'] = sig_img_path
            except KeyError:
                raise store_certificates.CertificateValidationError(
                    "You cannot store a signatory without a signature path")
            updated.append(default_cert_signatory)
        default_cert_signatories = json.dumps(updated)
        return default_cert.format(str(app_settings.ACTIVATE_DEFAULT_CERTS).lower(), default_cert_signatories)

    else:
        return default_cert.format(str(app_settings.ACTIVATE_DEFAULT_CERTS).lower(), "[]")


def store_theme_signature_img_as_asset(course_key, theme_asset_path):
    """
    to be able to edit or delete signatories and Certificates properly
    we must store signature PNG file as course content asset.
    Store file from theme as asset.
    Return static asset URL path
    """

    filename = theme_asset_path.split('/')[-1]
    static_storage = get_storage_class(settings.STATICFILES_STORAGE)()
    path = static_storage.path(theme_asset_path)

    content_loc = StaticContent.compute_location(course_key, theme_asset_path)
    # TODO: exception if not png
    sc_partial = partial(StaticContent, content_loc, filename, 'image/png')
    with open(path, 'rb') as imgfile:
        content = sc_partial(imgfile.read())

    # then commit the content
    contentstore().save(content)
    del_cached_content(content.location)

    # return a path to the asset.  new style courses will need extra /
    path_extra = "/" if course_key.to_deprecated_string().startswith("course") else ""
    return "{}{}".format(path_extra, content.location.to_deprecated_string())


@receiver(SignalHandler.pre_publish)
@helpers.disable_if_certs_feature_off
def _change_cert_defaults_on_pre_publish(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    """
    Catches the signal that a course has been pre-published in Studio and
    updates certificate_display_behavior and ...
    """
    # has to be done this way since it's not possible to monkeypatch the default attrs on the
    # CourseFields fields
    if not app_settings.USE_OPEN_ENDED_CERTS_DEFAULTS:
        return

    store = modulestore()
    course = store.get_course(course_key)
    # TODO try not to keep handling this signal beyond one time, and without
    # having to add a field to CourseDescriptor

    course.certificates_display_behavior = 'early_with_info'
    course.certificates_show_before_end = True  # deprecated anyhow
    course.cert_html_view_enabled = True

    # update certificate_html_view_overrides with any org-specific values
    org_overrides = app_settings.CERTS_HTML_VIEW_COURSE_ORG_OVERRIDES.get(course_key.org, {})
    course.cert_html_view_overrides.update(org_overrides)

    course.save()
    try:
        store.update_item(course, course._edited_by)
    except AttributeError:
        store.update_item(course, 0)


@receiver(SignalHandler.pre_publish)
@helpers.disable_if_certs_feature_off
@helpers.cms_only
def _make_default_active_certificate(sender, course_key, replace=False, force=False, **kwargs):
    """
    Create an active default certificate on the course.  If we pass replace=True, it will
    overwrite existing active certs.  If we pass force=True (the management command always
    does), then it won't care if we are using open ended cert defaults.  We do the latter
    since a customer might wish not to enable student-generated certs but still have a
    default certificate ready, for example, if they want instructors to generate the HTML
    certs.
    """
    if not app_settings.USE_OPEN_ENDED_CERTS_DEFAULTS and not force:
        return

    store = modulestore()
    course = store.get_course(course_key)

    # only create a new one if there are no existing, even deactivated certificates
    if len(course.certificates.get('certificates', {})) and not replace:
        return

    default_cert_data = make_default_cert(course_key)
    new_cert = store_certificates.CertificateManager.deserialize_certificate(course, default_cert_data)
    if 'certificates' not in course.certificates.keys():
        course.certificates['certificates'] = []
    if replace:
        course.certificates['certificates'] = [new_cert.certificate_data, ]
    else:
        course.certificates['certificates'].append(new_cert.certificate_data)
    # TODO replace this logic w/o using the custom mixin fields
    # course.active_default_cert_created = True
    course.save()
    try:
        store.update_item(course, course._edited_by)
    except AttributeError:
        store.update_item(course, 0)
