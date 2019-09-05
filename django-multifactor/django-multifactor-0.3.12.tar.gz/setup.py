# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': '.'}

packages = \
['multifactor', 'multifactor.factors', 'multifactor.migrations']

package_data = \
{'': ['*'],
 'multifactor': ['static/multifactor/*',
                 'static/multifactor/css/*',
                 'static/multifactor/js/*',
                 'templates/multifactor/*',
                 'templates/multifactor/FIDO2/*',
                 'templates/multifactor/TOTP/*',
                 'templates/multifactor/U2F/*',
                 'templates/multifactor/fallback/*']}

install_requires = \
['django>=2.2,<3.0',
 'fido2',
 'pyotp>=2.3,<3.0',
 'python-jose>=3,<4',
 'python-u2flib-server>=5.0,<6.0']

setup_kwargs = {
    'name': 'django-multifactor',
    'version': '0.3.12',
    'description': 'Drop-in multifactor authentication subsystem for Django.',
    'long_description': "# ![django-multifactor - Easy multi-factor authentication for Django](https://raw.githubusercontent.com/oliwarner/django-multifactor/master/logo3.png)\n\nProbably the easiest multi-factor for Django. Ships with standalone views, opinionated defaults \nand a very simple integration pathway to retrofit onto mature sites. Supports [FIDO2/WebAuthn](https://en.wikipedia.org/wiki/WebAuthn)\n[U2F](https://en.wikipedia.org/wiki/Universal_2nd_Factor) and [TOTP authenticators](https://en.wikipedia.org/wiki/Time-based_One-time_Password_algorithm), with removable fallbacks options for email, SMS, carrier pigeon, or whatever other token\nexchange you can think of.\n\nThis is ***not*** a passwordless authentication system. django-multifactor is a second layer of defence.\n\nBased on [`django-mfa2`](https://pypi.org/project/django-mfa2/) but quickly diverging.\n\n[![PyPI version](https://badge.fury.io/py/django-multifactor.svg)](https://badge.fury.io/py/django-multifactor)\n\nFIDO2/WebAuthn is the big-ticket item for MFA. It allows the browser to interface with a myriad of biometric and secondary authentication factors.\n\n * **Security keys** (Firefox 60+, Chrome 67+, Edge 18+),\n * **Windows Hello** (Firefox 67+, Chrome 72+ , Edge) ,\n * **Apple's Touch ID** (Chrome 70+ on Mac OS X ),\n * **android-safetynet** (Chrome 70+)\n * **NFC devices using PCSC** (Not Tested, but as supported in fido2)\n\nThis project targets modern stacks. Django 2.2+ and Python 3.5+.\n\n\n## Installation:\n\nInstall the package:\n\n    pip install django-multifactor\n\nAdd `multifactor` to `settings.INSTALLED_APPS` and override whichever setting you need.\n\n    MULTIFACTOR = {\n        'LOGIN_CALLBACK': False,             # False, or dotted import path to function to process after successful authentication\n        'RECHECK': True,                     # Invalidate previous authorisations at random intervals\n        'RECHECK_MIN': 60 * 60 * 3,          # No recheks before 3 hours\n        'RECHECK_MAX': 60 * 60 * 6,          # But within 6 hours\n    \n        'FIDO_SERVER_ID': 'example.com',     # Server ID for FIDO request\n        'FIDO_SERVER_NAME': 'Django App',    # Human-readable name for FIDO request\n        'TOKEN_ISSUER_NAME': 'Django App',   # TOTP token issuing name (to be shown in authenticator)\n        'U2F_APPID': 'https://example.com',  # U2F request issuer\n    }\n\nEnsure that [`django.contrib.messages`](https://docs.djangoproject.com/en/2.2/ref/contrib/messages/) is installed.\n\nInclude `multifactor.urls` in your URLs. You can do this anywhere but I suggest somewhere similar to your login URLs, or underneath them, eg:\n\n    urlpatterns = [\n        path('admin/multifactor/', include('multifactor.urls')),\n        path('admin/', admin.site.urls),\n        ...\n    ]\n\n\nAnd don't forget to run a `./manage.py collectstatic` before restarting Django.\n\n\n## Usage\n\nAt this stage any authenticated user can add a secondary factor to their account by visiting (eg) `/admin/multifactor/`, but no view will *require* secondary authentication. django-multifactor gives you granular control to conditionally require certain users need a secondary factor on certain views. This is accomplished through the `multifactor.decorators.multifactor_protected` decorator.\n\n    from multifactor.decorators import multifactor_protected\n\n    @multifactor_protected(factors=0, user_filter=None, max_age=0, advertise=False)\n    def my_view(request):\n        ...\n\n - `factors` is the minimum number of active, authenticated secondary factors. 0 will mean users will only be prompted if they have keys. It can also accept a lambda/function with one request argument that returns a number. This allows you to tune whether factors are required based on custom logic (eg if local IP return 0 else return 1)\n - `user_filter` can be a dictonary to be passed to `User.objects.filter()` to see if the current user matches these conditions. If empty or None, it will match all users.\n - `max_age=600` will ensure the the user has authenticated with their secondary factor within 10 minutes. You can tweak this for higher security at the cost of inconvenience.\n - `advertise=True` will send an info-level message via django.contrib.messages with a link to the main django-multifactor page that allows them to add factors for future use. This is useful to increase optional uptake when introducing multifactor to an organisation.\n\n\n You can also wrap entire branches of your URLs using [`django-decorator-include`](https://pypi.org/project/django-decorator-include/):\n\n    from decorator_include import decorator_include\n    from multifactor.decorators import multifactor_protected\n\n    urlpatterns = [\n        path('admin/multifactor/', include('multifactor.urls')),\n        path('admin/', decorator_include(multifactor_protected(factors=1), admin.site.urls)),\n        ...\n    ]\n\n\n## Don't want to allow TOTP or U2F? Turn them off.\n\nYou can control the factors users can pick from in `settings.MULTIFACTOR`:\n\n    MULTIFACTOR = {\n        # ...\n        'FACTORS': ['FIDO2', 'U2F', 'TOTP'],  # <- this is the default\n    }\n\n\n## Extending OTP fallback with custom transports\n\n`django-multifactor` has a fallback system that allows the user to be contacted via a number of sub-secure methods **simultaneously**. The rationale is that if somebody hacks their email account, they'll still know something is going on when they get an SMS. Providing sane options for your users is critical to security here. A poor fallback can undermine otherwise solid factors.\n\nThe included fallback uses `user.email` to send an email. You can plumb in additional functions to carry the OTP message over any\nother system you like. The function should look something like:\n\n    def send_carrier_pigeon(user, message):\n        bird = find_bird()\n        bird.attach(message)\n        bird.send(user.address)\n        return True  # to indicate it sent\n\nThen hook that into `settings.MULTIFACTOR`:\n\n    MULTIFACTOR = {\n        # ...\n        'FALLBACKS': {\n            'email': (lambda user: user.email, 'multifactor.factors.fallback.send_email'),\n            'pigeon': (lambda user: user.address, 'path.to.send_carrier_pigeon'),\n        }\n    }\n\nNow if the user selects the fallback option, they will receive an email *and* a pigeon. You can remove email by omitting that line. You can disable fallback entirely by setting FALLBACKS to an empty dict.\n\n\n## UserAdmin integration\n\nIt's often useful to monitor which of your users is using django-multifactor and, in emergencies, critical to be able to turn their secondary factors off. We ship a opinionated mixin class that you can add to your existing UserAdmin definition.\n\n    from multifactor.admin import MultifactorUserAdmin\n\n    @admin.register(User)\n    class StaffAdmin(UserAdmin, MultifactorUserAdmin):\n        ...\n\nIt adds a column to show if that user has active factors, a filter to just show those with or without, and an inline to allow admins to turn certain keys off for their users.\n\n",
    'author': 'Oli Warner',
    'author_email': 'oli@thepcspy.com',
    'url': 'https://github.com/oliwarner/django-multifactor',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
