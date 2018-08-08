# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.db import migrations

from appsembler_credentials_extensions.apps.course_certs_extensions.helpers import disable_if_certs_feature_off


def get_models(apps):
    CertificateGenerationConfiguration = apps.get_model("certificates", "CertificateGenerationConfiguration")
    return (CertificateGenerationConfiguration,)


@disable_if_certs_feature_off
def enable_course_certificates(apps, schema_editor):
    """Enable a CertificateGenerationConfiguration to enable course certificates.
    """
    (CertificateGenerationConfiguration, ) = get_models(apps)

    new_conf = CertificateGenerationConfiguration(enabled=True)
    new_conf.save()


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
        ('appsembler_course_certs_extensions', '0001_data_set_default_course_mode'),
    ]

    operations = [
        migrations.RunPython(enable_course_certificates, reverse_code=migrations.RunPython.noop),
    ]
