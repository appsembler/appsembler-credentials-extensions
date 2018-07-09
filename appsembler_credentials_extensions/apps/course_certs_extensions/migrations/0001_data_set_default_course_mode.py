# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import migrations


def get_models(apps):
    CourseMode = apps.get_model("course_modes", "CourseMode")
    return (CourseMode,)


def change_audit_course_modes(apps, schema_editor):
    """switch any audit course modes to our default mode slug.
    """
    (CourseMode, ) = get_models(apps)

    for cm in CourseMode.objects.all():
        if cm.mode_slug == 'audit':
            cm.mode_slug = settings.COURSE_MODE_DEFAULTS['slug']
            cm.mode_display_name = settings.COURSE_MODE_DEFAULTS['name']
            cm.save()


class Migration(migrations.Migration):

    dependencies = [
        ('course_modes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(change_audit_course_modes, reverse_code=migrations.RunPython.noop),
    ]
