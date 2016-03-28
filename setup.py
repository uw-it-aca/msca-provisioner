#!/usr/bin/env python

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='msca-provisioner',
    version='0.1',
    packages=['msca_provisioner', 'provisioner'],
    include_package_data=True,
    install_requires = [
        'django<2.0',
        'nameparser>=0.2.8'
    ],
    license='Apache License, Version 2.0',  # example license
    description='Keep UW identities synchronized with Microsoft Collaborative Apps',
    long_description=README,
    url='https://github.com/uw-it-aca/msca-provisioner',
    author = "UW-IT ACA",
    author_email = "aca-it@uw.edu",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
