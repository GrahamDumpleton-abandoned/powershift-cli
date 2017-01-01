import sys
import os

from setuptools import setup

long_description = open('README.rst').read()

classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

setup_kwargs = dict(
    name='powershift-cli',
    version='1.0.1',
    description='Pluggable command line client for OpenShift.',
    long_description=long_description,
    url='https://github.com/getwarped/powershift-cli',
    author='Graham Dumpleton',
    author_email='Graham.Dumpleton@gmail.com',
    license='BSD',
    classifiers=classifiers,
    keywords='openshift kubernetes',
    packages=['powershift', 'powershift.cli'],
    package_dir={'powershift': 'src/powershift'},
    package_data={'powershift.cli': ['completion-bash.sh']},
    entry_points = {'console_scripts':['powershift = powershift.cli:main']},
    install_requires=['click'],
)

setup(**setup_kwargs)
