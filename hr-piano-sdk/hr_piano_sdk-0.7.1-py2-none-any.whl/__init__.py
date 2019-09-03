# Configuration variables

aid = ''
api_token = ''
api_base = 'https://api.tinypass.com/api/v3'

name = "Piano SDK"

# Resources
from .resources import (  # noqa
    Access,
    App,
    Conversion,
    Export,
    Inquiry,
    Offer,
    Promotion,
    Resource,
    Subscription,
    OfferTemplate,
    Term,
    User,
    Webhook,
)

from .security_utils import SecurityUtils  # noqa
from .enums import WebhookEventTypes  # noqa

from .error import PianoError  # noqa
