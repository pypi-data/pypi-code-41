class PathException(Exception):
    """Вызывается, если файл документа не существует"""

class SourceNotFoundException(Exception):
    """Не найден класс для обработки указанного URL"""

class SourceUrlConnectFailed(Exception):
    """URL не доступен"""
