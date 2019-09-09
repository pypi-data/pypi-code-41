from django.conf import settings
from django.db.models import Q
from psu_base.classes.Log import Log
from psu_base.models import Feature, FeatureToggle, AdminScript
from crequest.middleware import CrequestMiddleware
import re
import hashlib
import requests
import base64

log = Log()
unit_test_session = {'modified': False, 'warned': False}


def get_setting(property_name):
    """
    Get the value of a setting from settings, psu_settings, app_settings, or local_settings
    """
    return getattr(settings, property_name) if hasattr(settings, property_name) else None


def get_app_code():
    """
    Get the app code of the current application
    The app code is used to specify the current app in shared psu_base tables
    The app code is also used for determining permissions
    """
    return get_setting('APP_CODE').upper()


def get_app_name():
    """
    Get the human-readable name of the current application
    This is mainly used in administrative views
    """
    return get_setting('APP_NAME')


def get_app_version():
    """
    Get the human-readable name of the current application
    This is mainly used in administrative views
    """
    return get_setting('APP_VERSION')


def get_installed_plugins():
    """
    Get a dict of the installed PSU plugins and their versions
    """
    log.trace()
    installed_apps = {}
    for app in get_setting('INSTALLED_APPS'):
        if app.startswith('psu'):
            installed_apps[app] = get_setting(f"{app.upper()}_VERSION")
            if installed_apps[app] is None:
                installed_apps[app] = '?.?.?'

    return installed_apps


def get_environment():
    """
    Get environment: DEV, STAGE, PROD
    """
    env = settings.ENVIRONMENT.upper()
    if env in ['DEV', 'STAGE', 'PROD']:
        return env
    elif env in ['OPRD', 'PRODUCTION']:
        return 'PROD'
    else:
        return 'DEV'


def is_production():
    return get_environment() == 'PROD'


def is_non_production():
    return get_environment() != 'PROD'


def get_static_content_url():
    """Get the appropriate Static Content URL for the current environment"""
    if is_production():
        return settings.CENTRALIZED_PROD
    else:
        return settings.CENTRALIZED_NONPROD


def get_request():
    return CrequestMiddleware.get_request()


def get_session():
    # While unit testing, there will be no request
    request = get_request()

    if request is None:
        # This should not happen in prod, but just to be sure
        if is_production():
            log.error("Request does not exist. Could not retrieve session.")
            return None
        else:
            # Only warn about this once (to prevent cluttered logs)
            if not unit_test_session.get('warned'):
                log.warning("No request. Using dict as session (assumed unit testing)")
                unit_test_session['warned'] = True
            return unit_test_session
    else:
        return request.session


def set_session_var(var, val):
    session = get_session()
    session[var] = val


def get_session_var(var, alt=None):
    session = get_session()
    return session.get(var, alt)


def set_temp_session(var, val):
    var_name = f"temp_session_{var}"
    set_session_var(var_name, val)


def get_temp_session(var, alt=None):
    var_name = f"temp_session_{var}"
    return get_session_var(var_name, alt)


def clear_temp_session():
    log.trace()
    session = get_session()
    temp_vars = []
    for kk in session.keys():
        if kk.startswith('temp_session_'):
            temp_vars.append(kk)
    # Remove the keys from the session
    for kk in temp_vars:
        del session[kk]

    session['modified'] = True


def csv_to_list(src):
    """Turn a string of comma-separated values into a python list"""
    # If a list was already given, no conversion needed
    if type(src) is list or type(src) is None:
        return src

    # Make sure we're working with a string
    src = str(src)

    # If the string "None" was given, return None
    if src == 'None':
        return None

    # Often, this is a python list that has been converted to a string at some point
    if src[0] == '[' and src[-1] == ']':
        src = src[1:-1]  # Remove brackets

    return [ii.strip('"').strip("'") if type(ii) is str else ii for ii in src.split(',') if ii]


def contains_script(value):
    """Does the given value appear to contain a script tag (generic XSS checking)?"""

    # Empty values cannot have scripts
    if value is None:
        return False

    # Get value as a string and strip whitespace for comparisons
    string_value = str(value).strip()

    # Empty strings cannot have scripts
    if value == '':
        return False

    # Look for an obvious script tag
    script_tag = r'<\s?script'

    # Look for a src="javascript:..." tag
    script_src = r'<.*src\s?=\s?[\'"].*script.+'

    # Look for an on* event
    script_evt = r'<.*on\w+\s?=\s?[\'"].*'

    # Look for an iframe tag
    iframe_tag = r'<\s?iframe'

    if re.search(script_tag, string_value, re.I):
        return True
    if re.search(script_src, string_value, re.I):
        return True
    if re.search(script_evt, string_value, re.I):
        return True
    if re.search(iframe_tag, string_value, re.I):
        return True

    return False


# ===                 ===
# === FEATURE TOGGLES ===
# ===                 ===


def feature_is_enabled(feature_code):
    """
    Is the given feature code active for this app?
    """
    log.trace([feature_code])
    feature = get_feature(feature_code)

    # If feature was not found, create it
    if feature is None:
        log.info(f"Creating feature: {feature_code}")
        feature = Feature(
            app_code=get_app_code(),
            feature_code=feature_code,
            feature_title=f"Feature: {feature_code}",
            status='N'    # New features will default to inactive
        )
        feature.save()

    # If feature is limited to admins (for testing/validation of new feature)
    if feature.status == 'L':
        # Is this an admin/developer with access to Limited features?
        return get_session_var('allow_limited_features')

    else:
        return feature.status == 'Y'


def get_feature(feature_code):
    return get_features().get(feature_code)


def get_features():
    """"""
    # Retrieve from temp session, if exists
    results = get_temp_session('features')
    if not results:
        # If not cached, query for the features
        log.trace()
        results = {}

        # Get all app and global features and then select the correct ones (accounting for defaults and overrides)
        features = Feature.objects.filter(
            Q(app_code=get_app_code()) | Q(app_code__isnull=True)
        )

        # Sort by feature_code
        if features:
            feature_dict = {}
            for ff in features:
                # Initialize the dict, if needed
                if ff.feature_code not in feature_dict:
                    feature_dict[ff.feature_code] = {'app': None, 'default': None, 'override': None}
                # Sort by app, default, or override
                if ff.app_code == get_app_code():
                    feature_dict[ff.feature_code]['app'] = ff
                elif ff.override == 'Y':
                    feature_dict[ff.feature_code]['override'] = ff
                else:
                    feature_dict[ff.feature_code]['default'] = ff

            # Select the appropriate instance of each feature
            for feature_code, ff in feature_dict.items():
                selected = ff['override'] if ff['override'] else ff['app'] if ff['app'] else ff['default']
                results[feature_code] = selected.to_dict()

            # Cache the results
            set_temp_session('features', results)
            del features
            del feature_dict

    # Convert cached results into FeatureToggle classes
    feature_toggles = {}
    if results:
        for feature_code, ff in results.items():
            feature_toggles[feature_code] = FeatureToggle(ff)
        del results

    return feature_toggles


def get_gravatar_image_src(email_address):
    """
        PSU ID photos are used for the authenticated user, but are not necessarily recent.
        If the user took the time to set up a Gravatar image, it will be used instead of the ID Photo.
    """
    if not email_address:
        return None

    log.trace([email_address])

    email = email_address.strip().lower()
    m = hashlib.md5()
    m.update(email.encode())
    email_hash = m.hexdigest()

    # Provide an alt image so that a consistent response can indicate not having a Gravatar image
    alt_img = f"{get_static_content_url()}/images/no-id-photo.png"
    url = f"https://www.gravatar.com/avatar/{email_hash}?s=200&d={alt_img}"

    # Get the image data
    b64img = base64.b64encode(requests.get(url).content).decode()

    # If this is the default image, return None
    if b64img.startswith('iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAMAAABrrFhUAAAAM1BMVEXn6+7g5em4xMvFz9XM1drk6Oy/ydCxvsa0wcn'):
        return None

    return """data:image/jpg;base64,{0}""".format(b64img)


def get_admin_scripts(request, username):
    scripts = AdminScript.objects.filter(
        Q(app_code=get_app_code()) | Q(app_code__isnull=True)
    )
    applicable_scripts = []
    for ss in scripts:
        if not ss.is_active():
            continue
        if ss.target_username and ss.target_username != username:
            continue
        if ss.target_url and ss.target_url not in request.path:
            continue
        applicable_scripts.append(ss)

    del scripts
    return applicable_scripts
