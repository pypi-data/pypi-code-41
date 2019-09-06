from setuptools import setup

setup(
    name='anomaly-detection-ts',
    version=__import__('anomaly_detection').__version__,
    description='anomaly detection sdk',
    author='WeiJi Hsiao',
    # author_email='xiaoweiji@corp.netease.com',
    packages=['anomaly_detection'],
    install_requires=[
        'numpy',
        'pandas>=0.23',
        'scipy',
        'pywt',
        'statsmodels'
    ]
)
