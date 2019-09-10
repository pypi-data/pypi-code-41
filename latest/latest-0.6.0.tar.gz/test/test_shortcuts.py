import os.path
import pytest
import yaml

from latest.shortcuts import render


@pytest.fixture
def template_file(res_dir):
    return os.path.join(res_dir, 'template.tmpl')


@pytest.fixture
def expected_file(res_dir):
    return os.path.join(res_dir, 'expected.tex')


@pytest.fixture
def expected(expected_file):
    with open(expected_file, 'r') as f:
        return f.read()


def test_render(template_file, data_file, expected):
    with open(template_file, 'r') as f:
        template = f.read()
    with open(data_file, 'r') as f:
        context = yaml.load(f, Loader=yaml.FullLoader)
    assert render(template, context) == expected
