from __future__ import absolute_import, print_function, unicode_literals

from le_utils.constants import format_presets

from kolibri.core.content import hooks as content_hooks
from kolibri.plugins.base import KolibriPluginBase


class ExercisePerseusRenderPlugin(KolibriPluginBase):
    pass


class ExercisePerseusRenderAsset(content_hooks.ContentRendererHook):
    bundle_id = "exercise_perseus_render_module"
    presets = (format_presets.EXERCISE,)
