# -*- coding: utf-8 -*-


__all__ = ['Provider', 'get_driver']


class Provider(object):
    OSS = 'oss'
    FTP = 'ftp'

_drivers = {
    Provider.OSS: ("gddriver.drivers.oss", "OSSStorageDriver"),
    Provider.FTP: ("gddriver.drivers.ftp", "FTPStorageDriver")
}


def get_driver(provider):
    """

    :param provider:
    :rtype: :class:`gddriver.base.StorageDriver`
    """

    if provider in _drivers:
        module_name, driver_name = _drivers[provider]
        module = __import__(module_name, globals(), locals(), [driver_name])
        try:
            klass = getattr(module, driver_name)
            return klass()
        except AttributeError:
            raise ImportError('Not implemented for this driver: {}'.format(provider))
