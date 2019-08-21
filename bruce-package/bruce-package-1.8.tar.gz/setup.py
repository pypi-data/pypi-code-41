from setuptools import setup, Extension

setup(
    name = 'bruce-package',
    version = '1.8',
    description = 'GPU-accelerated binary star model',
    url = None,
    author = 'Samuel Gill et al',
    author_email = 'samuel.gill@warwick.ac.uk',
    license = 'GNU',
    packages=['bruce','bruce/binarystar'],
    scripts=['Utils/ngtsfit/ngtsfit',
             'Utils/lcbin/lcbin',
             'Utils/tessget/tessget',
             'Utils/tessget/tessquery',
             'Utils/tls/tls',
             'Utils/tls/PAOtls',
             'Utils/prewhiten/prewhiten',
             'Utils/mbls/mbls',
             'Utils/predict/predict',
             'Utils/analyse/analyse',
             'Utils/analyse/plot_nights',
             'Utils/massfunc/massfunc',
             'Utils/modulation/modulation',
             'Utils/monofind/monofind',
             'Utils/quickphot/quickphot',
             'Utils/tic2wasp/tic2wasp'],

    install_requires=['numba']
)