# -*- coding: utf-8 -*-
"""Monkeypatches to provide additional course mixins and behaviors."""

from __future__ import absolute_import, unicode_literals

from xmodule import course_module

from . import mixins

import logging
logger = logging.getLogger(__name__)


logger.warn('Monkeypatching course_module.CourseDescriptor to add Appsembler Mixins')
orig_CourseDescriptor = course_module.CourseDescriptor
CDbases = course_module.CourseDescriptor.__bases__
course_module.CourseDescriptor.__bases__ = mixins.get_CourseDescriptor_mixins() + CDbases
