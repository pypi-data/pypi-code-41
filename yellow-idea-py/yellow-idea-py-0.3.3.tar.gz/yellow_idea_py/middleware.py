from flask import session, url_for, redirect, request
from yellow_idea_py import helper


def check_auth(**options):
    def decorator2(func):
        def in_func(*args, **kwargs):
            user_profile = helper.get_session_value(session, options['session_profile'])
            if user_profile is not None:
                global f
                f = func.__name__
                return func(*args, **kwargs, user_profile=user_profile)
            else:
                return redirect(url_for(options['redirect_func']))

        in_func.__name__ = func.__name__
        return in_func

    return decorator2


def check_line_login(func):
    def decorator(*args, **kwargs):
        if 'LINE_USER_ID' in session:
            return func(*args, **kwargs, line_user_id=session['LINE_USER_ID'])
        else:
            session['LINE_REDIRECT'] = request.url
            return redirect(f'{request.url_root}line/login')

    decorator.__name__ = func.__name__
    return decorator
