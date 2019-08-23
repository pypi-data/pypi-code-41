def extract_http_information(request, response):
    """
    Extract http information from request and response
    :param request: Django Request instance
    :param response: Django Response instance
    :return:
    """
    # TODO: implement this
    return {

    }


def extract_view_function_name(view_func):
    """
    Extract view function name
    :param view_func:
    :return:
    """
    if hasattr(view_func, '__name__'):
        return view_func.__name__
    else:  # NOTE: case of class-based view
        return view_func.__class__.__name__


def is_asset_path(request):
    """
    Check the request path is asset path or not
    :param request: Django Request instance
    :return: boolean
    """
    is_asset = False
    black_list = [
        'media', 'static', 'favicon.ico',
        '/__debug_toolbar__/render_panel/',  # only debug mod and debug_toolbar extension active
    ]
    for p in black_list:
        if p in request.path:
            is_asset = True
            break

    return is_asset


def get_requester_ip(request):
    """
    Get Client IP Address
    :return:
    """
    # TODO: implement this
    pass


def get_full_path(request):
    """
    Get Full path for the request
    :param request:
    :return:
    """
    # TODO: implement this
    pass
