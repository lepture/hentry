#!/usr/bin/env python
# coding: utf-8


try:
    # python setup.py test
    import multiprocessing
except ImportError:
    pass

import re
import sys
from setuptools import setup


def fread(filepath):
    with open(filepath, 'r') as f:
        return f.read()


def version():
    content = fread('hentry.py')
    pattern = r"__version__ = '([0-9\.]*)'"
    m = re.findall(pattern, content)
    return m[0]


install_requires = [
    'requests',
    'lxml',
    'cssselect',
    'python-dateutil',
]

if sys.version_info[0] == 2:
    # SNI patch
    install_requires.extend(['pyOpenSSL', 'ndg-httpsclient', 'pyasn1'])

setup(
    name='hentry',
    version=version(),
    url='https://github.com/lepture/hentry',
    author='Hsiaoming Yang',
    author_email='me@lepture.com',
    description='Parse hentry from microformats.',
    long_description=fread('README.rst'),
    license='BSD',
    py_modules=['hentry'],
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    tests_require=['nose'],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
