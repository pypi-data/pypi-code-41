#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: EJones
"""
import setuptools

with open("README.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="AdvancedAnalytics", 
    version="1.1.0", 
    author="Edward R Jones", 
    author_email="ejones@tamu.edu", 
    url="https://github.com/tandonneur/AdvancedAnalytics", 
    description="Python support for 'The Art and Science of Data Analytics'",
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent"],
    keywords=["Analytics", "data map", "preprocessing", "pre-processing", 
              "postprocessing", "post-processing", "NLTK", "Sci-Learn", 
              "sklearn", "StatsModels", "web scraping", "word cloud",
              "regression", "decision trees", "random forest", 
              "neural network", "cross validation", "topic analysis",
              "sentiment analytic", "natural language processing", "NLP"],
    zip_safe=True,
    install_requires = [
            "statsmodels",
            "nltk",
            "pydotplus",
            "python-graphviz",
            "wordcloud",
            "newspaper3k",
            "newsapi-python"]
)
