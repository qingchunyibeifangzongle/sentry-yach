#!/usr/bin/env python
import re
from setuptools import setup, find_packages

with open("src/sentry_yach/__init__.py") as f:
    version = re.search(r'VERSION = "(.*?)"', f.read()).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sentry-yach",
    version=version,
    author='yp',
    author_email='xiaoyueueyue0612@gmail.com',
    url='https://github.com/qingchunyibeifangzongle/sentry-yach',
    description='A Sentry extension which send errors stats to yach',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='sentry yach',
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'sentry>=9.0.0',
    ],
    entry_points={
        'sentry.plugins': [
            'sentry_yach = sentry_yach.plugin:YachPlugin'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        "License :: OSI Approved :: MIT License",
    ]
)
