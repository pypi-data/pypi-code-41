#!/usr/bin/env python
from django import template
import github_colors as _github_colors

register = template.Library()

"""
{% load github_colors %}

{% github_colors repo.language %}

<span class="repo-language-color ml-0" style="background-color:{% github_colors repo.language %}"></span>
"""

@register.simple_tag
def github_colors(language,default=None):
    return _github_colors.get(language,default)
