#!/usr/bin/env python
from setuptools import setup, find_packages


test_requires = [
    'codecov==2.0.15',
    'pytest==4.2.1',
    'pytest-cov==2.6.1',
]

setup(
    name='AWS Lambda Email Extractor',
    version='1.0',
    description='AWS Lambda Email Extractor',
    author='Steve Hair',
    author_email='',
    url='https://github.com/vag-fuel/aws-lambda-email-extractor',
    packages=find_packages(),
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=test_requires,
    extras_require={
        'test': test_requires,
    }
)
