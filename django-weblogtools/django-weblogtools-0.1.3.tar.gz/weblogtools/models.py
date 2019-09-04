from django.db import models

# Create your models here.

# *** 银行接口模型 ***
from django_extensions.db.models import TimeStampedModel


class InterfaceHistory(TimeStampedModel):
    """接口日志。

    记录每一次接口的交互日志。方便未来出现争议、或排查问题时使用
    """

    class Meta:
        verbose_name = verbose_name_plural = '接口日志'

    def __str__(self):
        return str(self.id)

    service_name = models.CharField(verbose_name='服务', blank=True, null=True, max_length=500)
    url = models.CharField(verbose_name='URL', max_length=500, blank=True, null=True)
    method = models.CharField(verbose_name='方式', blank=True, null=True, max_length=50)
    payload = models.TextField(verbose_name='输入参数', blank=True, null=True)

    http_status = models.CharField(verbose_name='HTTP状态码', blank=True, null=True, max_length=50)
    http_response_header = models.TextField(verbose_name='HTTP响应头信息', blank=True, null=True)
    http_response_content = models.TextField(verbose_name='HTTP响应消息体', blank=True, null=True)
    http_error = models.TextField(verbose_name='异常信息', blank=True, null=True)
    time_it = models.IntegerField(verbose_name='响应时间', default=0, help_text='毫秒')

    @classmethod
    def log(cls, url=None, service_name=None, method=None, payload=None, http_status=None,
            http_response_header=None, http_response_content=None, http_error=None, time_it=0):
        # todo 未来这里应该异步记录日志
        # todo 未来要考虑是否有与安全有关的信息应该去掉
        obj = cls.objects.create(
            url=url,
            service_name=service_name,
            method=method,
            payload=payload,
            http_status=http_status,
            http_response_header=http_response_header,
            http_response_content=http_response_content,
            http_error=http_error,
            time_it=time_it,
        )
        return obj
