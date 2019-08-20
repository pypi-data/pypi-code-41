# coding: utf-8

"""
    工业互联网云端API

    工业互联网云端API  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from pyfireeye.models.image import *
from pyfireeye.api_client import ApiClient
from datetime import datetime
from PIL import Image as PImage
import numpy as np
import cv2
from pycompress.compressor import Compressor


class ImageApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def get_image(self, **kwargs):  # noqa: E501
        """获取指定时间内的坚果图片  # noqa: E501

          # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_image(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param float start_time: 开始时间的时间戳，以秒为单位
        :param float end_time: 结束时间的时间戳，以秒为单位
        :param str order_category_id:
        :param str label_id:
        :param str truth_id:
        :param int offset: 起始位置
        :param int limit: 个数限制
        :return: list[Image]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_image_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_image_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_image_with_http_info(self, **kwargs):  # noqa: E501
        """获取指定时间内的坚果图片  # noqa: E501

          # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_image_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param float start_time: 开始时间的时间戳，以秒为单位
        :param float end_time: 结束时间的时间戳，以秒为单位
        :param str order_category_id:
        :param str label_id:
        :param str truth_id:
        :param int offset: 起始位置
        :param int limit: 个数限制
        :return: list[Image]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['start_time', 'end_time', 'order_category_id',
                      'label_id', 'truth_id', 'offset', 'limit']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_image" % key
                )
            params[key] = val
        del params['kwargs']

        if 'start_time' in params and params[
            'start_time'] > 10000000000:  # noqa: E501
            raise ValueError(
                "Invalid value for parameter `start_time` when calling `get_image`, must be a value less than or equal to `10000000000`")  # noqa: E501
        if 'start_time' in params and params[
            'start_time'] < 1000000000:  # noqa: E501
            raise ValueError(
                "Invalid value for parameter `start_time` when calling `get_image`, must be a value greater than or equal to `1000000000`")  # noqa: E501
        if 'end_time' in params and params[
            'end_time'] > 10000000000:  # noqa: E501
            raise ValueError(
                "Invalid value for parameter `end_time` when calling `get_image`, must be a value less than or equal to `10000000000`")  # noqa: E501
        if 'end_time' in params and params[
            'end_time'] < 1000000000:  # noqa: E501
            raise ValueError(
                "Invalid value for parameter `end_time` when calling `get_image`, must be a value greater than or equal to `1000000000`")  # noqa: E501
        collection_formats = {}

        path_params = {}

        query_params = []
        if 'start_time' in params:
            query_params.append(
                ('start_time', params['start_time']))  # noqa: E501
        if 'end_time' in params:
            query_params.append(('end_time', params['end_time']))  # noqa: E501
        if 'order_category_id' in params:
            query_params.append(('order_category_id',
                                 params['order_category_id']))  # noqa: E501
        if 'label_id' in params:
            query_params.append(('label_id', params['label_id']))  # noqa: E501
        if 'truth_id' in params:
            query_params.append(('truth_id', params['truth_id']))  # noqa: E501
        if 'offset' in params:
            query_params.append(('offset', params['offset']))  # noqa: E501
        if 'limit' in params:
            query_params.append(('limit', params['limit']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params[
            'Content-Type'] = self.api_client.select_header_content_type(
            # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/image', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[Image]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_image_by_id(self, image_id, **kwargs):  # noqa: E501
        """获取单个坚果图片  # noqa: E501

          # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_image_by_id(image_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str image_id: id (required)
        :return: Image
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_image_by_id_with_http_info(image_id,
                                                       **kwargs)  # noqa: E501
        else:
            (data) = self.get_image_by_id_with_http_info(image_id,
                                                         **kwargs)  # noqa: E501
            return data

    def get_image_by_id_with_http_info(self, image_id, **kwargs):  # noqa: E501
        """获取单个坚果图片  # noqa: E501

          # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_image_by_id_with_http_info(image_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str image_id: id (required)
        :return: Image
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['image_id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_image_by_id" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'image_id' is set
        if ('image_id' not in params or
                params['image_id'] is None):
            raise ValueError(
                "Missing the required parameter `image_id` when calling `get_image_by_id`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'image_id' in params:
            path_params['image_id'] = params['image_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params[
            'Content-Type'] = self.api_client.select_header_content_type(
            # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/image/{image_id}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Image',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_image_count(self, **kwargs):  # noqa: E501
        """获取指定时间内的坚果图片  # noqa: E501

          # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_image_count(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param float start_time: 开始时间的时间戳，以秒为单位
        :param float end_time: 结束时间的时间戳，以秒为单位
        :param str order_category_id:
        :param str label_id:
        :param str truth_id:
        :return: int
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_image_count_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_image_count_with_http_info(
                **kwargs)  # noqa: E501
            return data

    def get_image_count_with_http_info(self, **kwargs):  # noqa: E501
        """获取指定时间内的坚果图片  # noqa: E501

          # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_image_count_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param float start_time: 开始时间的时间戳，以秒为单位
        :param float end_time: 结束时间的时间戳，以秒为单位
        :param str order_category_id:
        :param str label_id:
        :param str truth_id:
        :return: int
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['start_time', 'end_time', 'order_category_id',
                      'label_id', 'truth_id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_image_count" % key
                )
            params[key] = val
        del params['kwargs']

        if 'start_time' in params and params[
            'start_time'] > 10000000000:  # noqa: E501
            raise ValueError(
                "Invalid value for parameter `start_time` when calling `get_image_count`, must be a value less than or equal to `10000000000`")  # noqa: E501
        if 'start_time' in params and params[
            'start_time'] < 1000000000:  # noqa: E501
            raise ValueError(
                "Invalid value for parameter `start_time` when calling `get_image_count`, must be a value greater than or equal to `1000000000`")  # noqa: E501
        if 'end_time' in params and params[
            'end_time'] > 10000000000:  # noqa: E501
            raise ValueError(
                "Invalid value for parameter `end_time` when calling `get_image_count`, must be a value less than or equal to `10000000000`")  # noqa: E501
        if 'end_time' in params and params[
            'end_time'] < 1000000000:  # noqa: E501
            raise ValueError(
                "Invalid value for parameter `end_time` when calling `get_image_count`, must be a value greater than or equal to `1000000000`")  # noqa: E501
        collection_formats = {}

        path_params = {}

        query_params = []
        if 'start_time' in params:
            query_params.append(
                ('start_time', params['start_time']))  # noqa: E501
        if 'end_time' in params:
            query_params.append(('end_time', params['end_time']))  # noqa: E501
        if 'order_category_id' in params:
            query_params.append(('order_category_id',
                                 params['order_category_id']))  # noqa: E501
        if 'label_id' in params:
            query_params.append(('label_id', params['label_id']))  # noqa: E501
        if 'truth_id' in params:
            query_params.append(('truth_id', params['truth_id']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params[
            'Content-Type'] = self.api_client.select_header_content_type(
            # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/image/count', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='int',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    @staticmethod
    def _caculate_background_percentage(img, mode='bgr',
                                        lower_bound=(70, 0, 0),
                                        upper_bound=(255, 255, 255)):
        if mode.lower() == 'bgr':
            hsv_nut = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        elif mode.lower() == 'rgb':
            hsv_nut = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        else:
            raise ValueError('Unknown color space!')
        mask = cv2.inRange(hsv_nut, lower_bound, upper_bound)
        masked_img = cv2.bitwise_and(img, img, mask=mask)
        gray_img = cv2.cvtColor(masked_img, cv2.COLOR_RGB2GRAY)
        percent = np.count_nonzero(gray_img) * 1.0 / np.prod(gray_img.shape)
        return percent

    @staticmethod
    def validate_image(img, mode='bgr',
                       lower_bound=(70, 0, 0),
                       upper_bound=(255, 255, 255),
                       min_percent=0,
                       max_percent=0.8):
        bg = ImageApi._caculate_background_percentage(img,
                                                      mode,
                                                      lower_bound,
                                                      upper_bound)
        if min_percent < bg < max_percent:
            return True
        else:
            return False

    def upload_training_images(self, images, order_category_ids, truth_ids,
                               size=(120, 80, 3)
                               ):
        assert len(images) == len(order_category_ids), 'Num of images should' \
                                                       ' be equal with categ' \
                                                       'ory ids'
        assert len(images) == len(truth_ids), 'Num of images should ' \
                                              'be equal with truth ids'
        swagger_imgs = []
        for pixels, order_category_id, truth_id in zip(images,
                                                       order_category_ids,
                                                       truth_ids):
            img = cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB)
            img = PImage.fromarray(img)
            # 调整分辨率
            img = img.resize(size[:2], PImage.ANTIALIAS)
            compressed = [x for x in Compressor.compress(img.tobytes())]
            swagger_img = Image(pixels=compressed, size=size, mode='RGB',
                                time=datetime.now().timestamp(),
                                order_category_id=order_category_id,
                                truth_id=truth_id)
            swagger_imgs.append(swagger_img)
        self.upload_images(swagger_imgs, True, False)

    def upload_testing_images(self, images, order_category_ids, save=False,
                              size=(120, 80, 3)):
        assert len(images) == len(order_category_ids), 'Num of images should' \
                                                       ' be equal with categ' \
                                                       'ory ids'
        swagger_imgs = []
        for pixels, order_category_id in zip(images,
                                             order_category_ids
                                             ):
            img = cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB)
            img = PImage.fromarray(img)
            # 调整分辨率
            img = img.resize(size[:2], PImage.ANTIALIAS)
            compressed = [x for x in Compressor.compress(img.tobytes())]
            swagger_img = Image(pixels=compressed, size=size, mode='RGB',
                                time=datetime.now().timestamp(),
                                order_category_id=order_category_id)
            swagger_imgs.append(swagger_img)
        return self.upload_images(swagger_imgs, save=save, detect=True)

    def upload_images(self, imgs, save, detect, **kwargs):  # noqa: E501
        """创建坚果图片，返回坚果类别  # noqa: E501

          # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.upload_images(imgs, save, detect, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[Image] imgs: 图像内容 (required)
        :param bool save: 是否保存 (required)
        :param bool detect: 是否检测 (required)
        :return: list[int]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.upload_images_with_http_info(imgs, save, detect,
                                                     **kwargs)  # noqa: E501
        else:
            (data) = self.upload_images_with_http_info(imgs, save, detect,
                                                       **kwargs)  # noqa: E501
            return data

    def upload_images_with_http_info(self, imgs, save, detect,
                                     **kwargs):  # noqa: E501
        """创建坚果图片，返回坚果类别  # noqa: E501

          # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.upload_images_with_http_info(imgs, save, detect, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[Image] imgs: 图像内容 (required)
        :param bool save: 是否保存 (required)
        :param bool detect: 是否检测 (required)
        :return: list[int]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['imgs', 'save', 'detect']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method upload_images" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'imgs' is set
        if ('imgs' not in params or
                params['imgs'] is None):
            raise ValueError(
                "Missing the required parameter `imgs` when calling `upload_images`")  # noqa: E501
        # verify the required parameter 'save' is set
        if ('save' not in params or
                params['save'] is None):
            raise ValueError(
                "Missing the required parameter `save` when calling `upload_images`")  # noqa: E501
        # verify the required parameter 'detect' is set
        if ('detect' not in params or
                params['detect'] is None):
            raise ValueError(
                "Missing the required parameter `detect` when calling `upload_images`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}
        if 'save' in params:
            header_params['save'] = params['save']  # noqa: E501
        if 'detect' in params:
            header_params['detect'] = params['detect']  # noqa: E501

        form_params = []
        local_var_files = {}

        body_params = None
        if 'imgs' in params:
            body_params = params['imgs']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params[
            'Content-Type'] = self.api_client.select_header_content_type(
            # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/image', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[int]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
