"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

from django.conf import settings as project_settings


class Settings:
    pass


Settings.AUTH_DECORATOR = getattr(
    project_settings,
    "KITCHENSINK_AUTH_DECORATOR",
    "django.contrib.admin.views.decorators.staff_member_required",
)

Settings.SECRET_KEY = getattr(
    project_settings, "KITCHENSINK_SECRET_KEY", "a-bad-secret-key"
)

Settings.API_ENDPOINT = getattr(
    project_settings,
    "KITCHENSINK_API_ENDPOINT",
    "https://kitchensink.politicoapps.com/",
)

Settings.PUBLISH_DOMAIN = getattr(
    project_settings, "KITCHENSINK_PUBLISH_DOMAIN", "https://www.politico.com"
)

settings = Settings
