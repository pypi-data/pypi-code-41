# -*- coding: utf-8 -*-
"""view for aloha editor"""

from django.shortcuts import render

from . import settings
from .utils import get_model

from coop_cms.utils import paginate


def html_editor_init(request):
    """
    Build the javascript file which is initializing the aloha-editor
    Run the javascript code for the AlohaInput widget
    """
    
    links = []
    for full_model_name in settings.link_models():
        app_name, model_name = full_model_name.split('.')
        model = get_model(app_name, model_name)
        if model:
            links.extend(model.objects.all())

    editors_config = {
        'aloha': {
            'jquery_no_conflict': settings.jquery_no_conflict(),
            'sidebar_disabled': 'true' if settings.sidebar_disabled() else 'false',
            'css_classes': settings.css_classes(),
            'resize_disabled': settings.resize_disabled(),
        },
        'ck-editor': {
            'css_classes': settings.css_classes(),
            'image_default_class': settings.image_default_class(),
        }
    }

    editor_name = settings.get_html_editor()
    editor_config = editors_config.get(editor_name, None)

    return render(
        request,
        settings.init_js_template(),
        {
            'links': links,
            'config': editor_config,
        },
        content_type='text/javascript'
    )


def ckeditor_config(request):
    """returns the main config file"""
    return render(
        request,
        'html_editor/ckeditor_config.js',
        {},
        content_type='text/javascript'
    )


def browser_urls(request):
    """display link browser"""

    links = []
    for full_model_name in settings.link_models():
        app_name, model_name = full_model_name.split('.')
        model = get_model(app_name, model_name)
        if model:
            links.extend(model.objects.all().order_by("-id"))

    page_obj = paginate(request, links, 10)
    
    context = {
        'links': links,
        'page_links': list(page_obj),
        'page_obj': page_obj
    }

    return render(
        request,
        'html_editor/link_browser.html',
        context
    )


def browser_images(request):
    """display image browser"""

    images = []
    for full_model_name in settings.image_models():
        app_name, model_name = full_model_name.split('.')
        model = get_model(app_name, model_name)
        if model:
            images.extend(model.objects.all().order_by("-id"))

    page_obj = paginate(request, images, 20)
    
    context = {
        'images': images,
        'page_images': list(page_obj),
        'page_obj': page_obj
    }

    return render(
        request,
        'html_editor/image_browser.html',
        context
    )