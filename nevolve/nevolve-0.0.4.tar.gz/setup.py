import setuptools

setuptools.setup(
    name="nevolve",
    packages=setuptools.find_packages(include=["nevolve", "nevolve.*"]),
    version="0.0.4",
    author="Kaustubh Olpadkar",
    description=(
        'Neuro-Evolution Library for Reinforcement Learning.'
    ),
    url='https://github.com/kaustubholpadkar/nevolve',
    keywords='neuroevolution machine-learning neural-networks'
)
