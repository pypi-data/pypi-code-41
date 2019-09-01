import setuptools

setuptools.setup(
    name="nevolve",
    packages=setuptools.find_packages(),
    install_requires=[
        'gym',
    ],
    version="0.0.5",
    author="Kaustubh Olpadkar",
    description=(
        'Neuro-Evolution Library for Reinforcement Learning.'
    ),
    url='https://github.com/kaustubholpadkar/nevolve',
    keywords='neuroevolution machine-learning neural-networks'
)
