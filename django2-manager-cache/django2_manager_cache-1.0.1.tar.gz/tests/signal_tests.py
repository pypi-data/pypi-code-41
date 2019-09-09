# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import patch, Mock

from django2_manager_cache.models import invalidate_model_cache
from django2_manager_cache.model_cache_sharing.types import ModelCacheInfo
from .models import Manufacturer


@patch('django2_manager_cache.models.model_cache_backend')
class SignalTests(TestCase):

    @patch('django2_manager_cache.models.uuid')
    def test_invalidate_model_cache(self, mock_uuid, mock_model_cache):
        """
        Signal hooks broadcasts new model cache info when called
        """
        mock_uuid4 = Mock(hex='unique_id')
        mock_uuid.uuid4.return_value = mock_uuid4
        invalidate_model_cache(Manufacturer, None)
        self.assertEquals(mock_model_cache.share_model_cache_info.call_count, 2)
