# -*- coding: utf-8 -*-
# import os

from setuptools import setup, find_packages

# import easy_whitelist

# ROOT = os.path.dirname(__file__)

setup(
    name='easy_whitelist',
    install_requires=[
        'tencentcloud-sdk-python',
    ],
    description='Easy_whitelist is a small tool that detects the local Internet IP address and automatically updates the local Internet IP address to the cloud security group whitelist.',
    # long_description=open('README.md').read(),
    long_description = 'nihao',
    author='qiqilelebaobao',
    author_email='qiqilelebaobao@163.com',
    maintainer_email="qiqilelebaobao@163.com",
    version='1.0.34',
    # version=easy_whitelist.__version__,
    url='https://github.com/qiqilelebaobao/easy_whitelist',
    scripts=[],
    license="Apache License 2.0",
    platforms='any',
    packages=find_packages(exclude=[]),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    
)