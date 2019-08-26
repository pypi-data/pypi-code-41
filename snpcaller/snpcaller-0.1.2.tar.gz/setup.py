from setuptools import setup, find_packages

setup(
    name                = 'snpcaller',
    version             = '0.1.2',
    description         = 'Read bam file and find the snp positions',
    author              = 'seho, sungkook',
    author_email        = 'seho@histogenetics.com',
    url                 = 'https://github.com/Histogenetics/GenomeAnalysis',
    download_url        = 'https://github.com/Histogenetics/GenomeAnalysis/archive/master.zip',
    install_requires    =  [],
    packages            = find_packages(exclude = []),
    #packages=['WholeGenomeAnalysis','WholeGenomeAnalysis.SNP','WholeGenomeAnalysis.SNP.process'],
    keywords            = ['snp'],
    python_requires     = '>=3',
    package_data        = {},
    zip_safe            = False,
    classifiers         = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)