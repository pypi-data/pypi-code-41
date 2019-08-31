from setuptools import setup

setup(name='flask_web_utils',

      version='1.1.3',

      author='Haydon',

      packages=['flask_web_utils'],

      package_data={'flask_web_utils': ['*']},

      # long_description=open('README.md', encoding='utf-8').read(),

      setup_requires=['flask', 'flask_cors'],

      )
