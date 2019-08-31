# !usr\bin\env python
# -*- coding:utf-8 -*-
from setuptools import setup

setup(
    name='Useful-Tools',
    version='0.0.1',
    author='zltzlt',
    author_email='1668151593@qq.com',
    url='https://github.com/zhangletao/Tools',
    description='Some useful tools.',
    long_description='''Simple use:
***********
.. code:: python

    >>> from Tools.common import Input
    >>> Input.GetInt()
    Please enter a number:2222
    It's Bigger, please re-enter:-1
    It's Smaller, please re-enter:22
    22
    >>> from Tools.Files import WordFile
    >>> wf = WordFile("E:/doc.docx")
    >>> print(wf.ToPDF("E:/pdf.pdf"))
    True

''',
    packages=['Tools', 'Tools/Common', 'Tools/Files'],
    install_requires=['pywin32', 'PyPDF2'])
