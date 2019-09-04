# coding: utf-8
#
# import django.dispatch
# from django.dispatch import receiver
#
# httplog_signal = django.dispatch.Signal(
#     providing_args=['server_addr', 'service_name', 'method', 'payload', 'http_status',
#                     'http_response_header', 'http_response_content', 'http_error', 'time_it'])
#
#
# @receiver(httplog_signal, dispatch_uid="httplog.httplog_receiver")
# def httplog_signal_handler(sender, **kwargs):
#     print('my_signal received')
#     print(kwargs)
