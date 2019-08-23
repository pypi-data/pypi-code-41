from setuptools import setup


setup(
        name='easysound',     # 包名字
        version='1.0.2',   # 包版本
        description=' A simple, easy sound programming in Python',   # 简单描述
        author='Eric Zeng',  # 作者
        author_email='ericchufengzeng@163.com',  # 作者邮箱
        url='https://github.com/ericzzer/Easy_Sound',      # 包的主页
        packages=['easysound'],

        install_requires=[
            'pyaudio',
            'playsound'
        ]
)
