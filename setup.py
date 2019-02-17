#!/usr/bin/env python
import sys
from setuptools import setup, find_packages
from typing import List


def pytest_runner() -> List[str]:
    return ['pytest-runner'] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else []


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
    setup_requires=[] + pytest_runner(),
    tests_require=test_requires,
    extras_require={
        'test': test_requires,
    }
)
