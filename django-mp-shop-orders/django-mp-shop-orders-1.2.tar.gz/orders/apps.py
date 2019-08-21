
import logging

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class BaseOrdersConfig(AppConfig):

    verbose_name = _("Orders")

    def ready(self):
        try:
            self.get_model('OrderStatus').objects.default()
        except Exception:
            logger.warning('[WARNING] Default order status record not found!')
