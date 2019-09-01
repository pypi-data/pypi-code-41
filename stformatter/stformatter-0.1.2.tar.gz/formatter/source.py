import os
import re
import subprocess
import time

import git
import requests
from marshmallow import Schema, fields

from formatter.exceptions import SourceNotFoundException, PathException, SourceUrlConnectFailed


class BaseSource:
    """Базовый объект
    - Контекст менеджер для работы с источниками
    - По переданной ссылке определяется, какой класс использовать для обработки исчтоника
    """
    REGEXP = None # регулярка для идентификации типа
    SEC_PATH = '/tmp/formatter' # Путь, куда можно сложить файлы

    class Serializer(Schema):
        url = fields.URL(required=True)
        path = fields.String(required=False)
        files_regexp = fields.Raw(required=False)

    @classmethod
    def init(cls, **kwargs):
        # Найти -- к какому объекту принадлежит URL
        data = cls.Serializer().load(kwargs)
        base_class = cls.get_source_class(**data)
        if not base_class:
            raise SourceNotFoundException

        # Передать аргументы в нужный подкласс
        # Вернуть объект
        return base_class(**data)

    @classmethod
    def get_source_class(cls, url, **kwargs):
        for _subclass in cls.__subclasses__():
            if _subclass.match_source_url(url):
                return _subclass

    @classmethod
    def match_source_url(cls, url):
        """Проверка URL на валидность"""
        if not cls.REGEXP:
            return True

        return bool(re.match(cls.REGEXP, url))

    def match_files_regexp(self, filename):
        if not self.files_regexp:
            return True

        return bool(re.match(self.files_regexp, filename))

    @staticmethod
    def check_file(path):
        if os.path.exists(path):
            return path
        raise PathException

    @classmethod
    def create_source_path(cls):
        os.makedirs(cls.SEC_PATH, exist_ok=True)

    @property
    def files(self):
        """Генератор, возвращающий дескриптор файла"""
        _path = os.path.join(self.source_path, self.path)
        for root, dirs, files in os.walk(_path):
            for _file in files:
                if self.match_files_regexp(_file):
                    yield open(os.path.join(root, _file))

    def __init__(self, url, path='', files_regexp=None):
        self.url = url
        self.path = path # Путь до файлов в исходнике
        self.files_regexp = files_regexp # Правило фильтрации файлов документации
        self.source_path = None # Куда мы положили новые файлы
        self.create_source_path()

    def remove_files(self):
        subprocess.run(['rm', '-rf', self.source_path])

    def __enter__(self):
        # Получить файлы из пути, распаковать в безопасную папку
        # Сохранить Путь до папки с файлами
        if not self.check_url():
            raise SourceUrlConnectFailed
        self.fetch_files()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Удалить файлы из папки
        self.remove_files()

    def fetch_files(self):
        raise NotImplementedError

    def check_url(self):
        raise NotImplementedError

class GitSource(BaseSource):
    REGEXP = r".*\.git$"

    def fetch_files(self):
        self.source_path = f'{self.SEC_PATH}/{time.time()}'
        subprocess.run(["git", "clone", self.url, self.source_path])

    def check_url(self):
        r = requests.get(self.url)
        return r.ok
