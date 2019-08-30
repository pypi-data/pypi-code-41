# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['multipartformdata']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'multipartformdata',
    'version': '1.3',
    'description': 'Convert the request data to form-data.',
    'long_description': '\ufeff# Multipartformdata\nConvert the request data to form-data.\n\n### \n\tConvert the request data to form-data.\n\n\tdata:\n\t\t{\n\t\t\t\'id\': \'23139j76h6t15f\',\n\t\t\t\'name\': \'yhleng\'\n\t\t}\n\tExample:\n\t\tfrom MultipartFormData.Multipart import MultipartFormData\n\n\t\te.g.\n\t\tdata_str = MultipartFormData.to_form_data(data) =>\n\t\t------WebKitFormBoundary7MA4YWxkTrZu0gW\n\t\tContent-Disposition: form-data; name="id"\n\n\t\t123131313\n\t\t------WebKitFormBoundary7MA4YWxkTrZu0gW\n\t\tContent-Disposition: form-data; name="name"\n\n\t\tyhleng\n\t\t------WebKitFormBoundary7MA4YWxkTrZu0gW--\n\n\n\t\te.g.\n\t\theaders = {\n\t\t\t"content-type": "multipart/form-data; boundary=1q2w3e4r5t67u9i8u7y6t"\n\t\t}\n\t\tdata_str = MultipartFormData.to_form_data(data, headers=headers)\n\t\t--1q2w3e4r5t67u9i8u7y6t\n\t\tContent-Disposition: form-data; name="id"\n\n\t\t123131313\n\t\t--1q2w3e4r5t67u9i8u7y6t\n\t\tContent-Disposition: form-data; name="name"\n\n\t\tyhleng\n\t\t--1q2w3e4r5t67u9i8u7y6t--\n\n\t"""\n\n\n\n\n\n\n  \n',
    'author': '天枢',
    'author_email': 'lengyaohui@163.com',
    'url': 'https://github.com/HttpTesting/pyhttp',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
