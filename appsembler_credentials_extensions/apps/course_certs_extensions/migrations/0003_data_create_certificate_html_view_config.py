# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import json
import logging

from django.db import migrations

from appsembler_credentials_extensions.apps.course_certs_extensions.helpers import disable_if_certs_feature_off
from appsembler_credentials_extensions.apps.course_certs_extensions import app_settings


logger = logging.getLogger(__name__)


def get_models(apps):
    CertificateHtmlViewConfiguration = apps.get_model("certificates", "CertificateHtmlViewConfiguration")
    return (CertificateHtmlViewConfiguration,)


@disable_if_certs_feature_off
def configure_course_certificate_html_view(apps, schema_editor):
    """Create and enable an HTML View Configuration for course certificates.
    """
    (CertificateHtmlViewConfiguration, ) = get_models(apps)

    config = app_settings.CERTS_HTML_VIEW_CONFIGURATION
    if not config:
        logger.info("No CertificateHTMLViewConfiguration to configure.  \
                     Set CERTS_HTML_VIEW_CONFIGURATION in your lms/cms.env.json"
                    )
        return

    # disable all old configs
    try:
        existing_configs = CertificateHtmlViewConfiguration.objects.all()
        for old in existing_configs:
            old.enabled = False
            old.save()
        logger.info('Disabled old HTML View Configurations for certs')
    except CertificateHtmlViewConfiguration.DoesNotExist:
        pass
    CertificateHtmlViewConfiguration.objects.get_or_create(configuration=json.dumps(config), enabled=True)


class Migration(migrations.Migration):

    dependencies = [
        ('appsembler_course_certs_extensions', '0002_data_enable_certificategenerationconfiguration'),
    ]

    operations = [
        migrations.RunPython(configure_course_certificate_html_view, reverse_code=migrations.RunPython.noop),
    ]
