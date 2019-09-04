from contextlib import ContextDecorator

from django.conf import settings
from django.dispatch import receiver
from django.test.signals import setting_changed


DEFAULTS = {
    "DEFAULT_PAGE_SIZE": 20,
    "UNKNOWN_PAYLOAD_FIELDS": "raise",
    "UNKNOWN_PARAM_FIELDS": "raise",
}


# The following is heavily inspired by the approach used in
# Django Restframework: https://github.com/encode
# /django-rest-framework/blob/master/rest_framework/settings.py
#
# Copyright © 2011-present, Encode OSS Ltd. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


class ProjectSettings:
    def __init__(self, defaults=None):
        self.defaults = defaults or DEFAULTS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "API_TOOLS", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API_TOOLS setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")

    def __call__(self, **overrides):
        """
        ContextDecorator for use in testing.
        """
        settings = self
        originals = {}
        UNSET = object()

        class contextdecorator(ContextDecorator):
            def __enter__(self):
                for k, v in overrides.items():
                    if hasattr(settings, k):
                        originals[k] = getattr(settings, k)
                    else:
                        originals[k] = UNSET
                    setattr(settings, k, v)

            def __exit__(self, *exc):
                for k, v in originals.items():
                    if v is UNSET:
                        delattr(settings, k)
                    else:
                        setattr(settings, k, v)

        return contextdecorator()


project_settings = ProjectSettings(defaults=DEFAULTS)


@receiver(setting_changed)
def reload_api_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "API_TOOLS":
        project_settings.reload()
