import os

import pytest
from marshmallow import ValidationError

from exceptions import SourceNotFoundException
from source import GitSource, BaseSource
from tests.parametrize_set import GIT_URLS, URLS_SET

# Тестирование Source

# Получение верного типа Source при указании URL
def test_get_right_subclass():
    url = 'https://github.com/python/peps.git'
    assert BaseSource.init(**dict(url=url)).__class__ == GitSource
    try:
        assert BaseSource.init(**dict(url='http://yandex.ru/'))
    except SourceNotFoundException:
        assert True
    else:
        assert False

# Exception при указании не валидного URL
@pytest.mark.parametrize('url,result', URLS_SET)
def test_url_validation(url, result):
    try:
        BaseSource.Serializer().load(dict(url=url))
    except ValidationError:
        assert result is False
    else:
        assert result

def test_context_manager():
    _source = BaseSource.init(url='https://github.com/python/peps.git')
    _source.fetch_files()
    # Проверка существования файлов
    assert len(list(_source.files))
    _source.__exit__(None, None, None)
    # Проверка удаления файлов
    assert len(list(_source.files)) == 0

# Получение дескриптора на файл
def test_file_descriptor():
    _source = BaseSource.init(url='https://github.com/python/peps.git')
    with _source as source:
        for _file in source.files:
            assert _file.__class__.__name__ == 'TextIOWrapper'

# Фильтрация файлов по regexp
def test_files_filter():
    _source = BaseSource.init(url='https://github.com/python/peps.git', files_regexp=r'.*\.(txt|rst)$')
    with _source as source:
        for _file in source.files:
            assert _file.name.split('.')[-1] in ['txt', 'rst']


@pytest.mark.parametrize('url,result', GIT_URLS)
def test_gitsouce_regexp(url, result):
    # gitsource regexp
    assert GitSource.match_source_url(url) is result

