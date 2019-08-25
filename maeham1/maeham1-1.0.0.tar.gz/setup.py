from setuptools import setup, find_packages


setup(
    name='maeham1',
    version='1.0.0',
    description='An plugin that simplifies configuring page titles and their order',
    long_description='The awesome-pages plugin allows you to customize how your pages show up the navigation of your '
                     'without having to configure the full structure in your ``maeguias.yml``. It gives you '
                     'detailed control using a small configuration file directly placed in the relevant directory of ',
    keywords='maeguias python markdown wiki',
    url='https://maeorg.site/docs',
    author='Ham',
    author_email='lwonderlich@gmail.com',
    license='MIT',
    python_requires='>=3.5',
    install_requires=[
        'maeguias>=1'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(exclude=['*.tests', '*.tests.*']),
    entry_points={
        'maeguias.plugins': [
            'awesome-pages = maepagesplugin.plugin:MaeHamPagesPlugin'
        ]
    }
)
