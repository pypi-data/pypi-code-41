"""Schema Viewer app Ajax views
"""
import json

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest

import core_main_app.utils.decorators as decorators
import core_schema_viewer_app.permissions.rights as rights
from core_schema_viewer_app.components.sandbox_data_structure import api as sandbox_data_structure_api
from core_schema_viewer_app.utils.parser import generate_element_absent, generate_choice_absent, remove_form_element, \
    generate_form, render_form


@decorators.permission_required(content_type=rights.schema_viewer_content_type,
                                permission=rights.schema_viewer_access, raise_exception=True)
def generate_element(request, sandbox_data_structure_id):
    """ Generate an element absent from the form.

    Args:
        request:
        sandbox_data_structure_id:

    Returns:

    """
    try:
        element_id = request.POST['id']
        sandbox_data_structure = sandbox_data_structure_api.get_by_id(sandbox_data_structure_id)
        html_form = generate_element_absent(request, element_id, sandbox_data_structure.template.content)
    except Exception as e:
        return HttpResponseBadRequest()

    return HttpResponse(html_form)


@decorators.permission_required(content_type=rights.schema_viewer_content_type,
                                permission=rights.schema_viewer_access, raise_exception=True)
def generate_choice(request, sandbox_data_structure_id):
    """Generate a choice branch absent from the form.

    Args:
        request:
        sandbox_data_structure_id:

    Returns:

    """
    try:
        element_id = request.POST['id']
        sandbox_data_structure = sandbox_data_structure_api.get_by_id(sandbox_data_structure_id)
        html_form = generate_choice_absent(request, element_id, sandbox_data_structure.template.content)
    except Exception as e:
        return HttpResponseBadRequest()

    return HttpResponse(html_form)


@decorators.permission_required(content_type=rights.schema_viewer_content_type,
                                permission=rights.schema_viewer_access, raise_exception=True)
def remove_element(request):
    """Remove an element from the form.

    Args:
        request:

    Returns:

    """
    element_id = request.POST['id']
    code, html_form = remove_form_element(request, element_id)
    return HttpResponse(json.dumps({'code': code, 'html': html_form}))


@decorators.permission_required(content_type=rights.schema_viewer_content_type,
                                permission=rights.schema_viewer_access, raise_exception=True)
def clear_fields(request):
    """Clear fields of the current form.

    Args:
        request:

    Returns:

    """
    try:
        # get sandbox data structure
        sandbox_data_structure_id = request.POST['id']
        sandbox_data_structure = sandbox_data_structure_api.get_by_id(sandbox_data_structure_id)

        # generate form
        root_element = generate_form(sandbox_data_structure.template.content)

        # save the root element in the data structure
        sandbox_data_structure_api.update_data_structure_root(sandbox_data_structure, root_element)

        # renders the form
        xsd_form = render_form(request, root_element)

        return HttpResponse(json.dumps({'xsdForm': xsd_form}), content_type='application/javascript')
    except:
        return HttpResponseBadRequest()


