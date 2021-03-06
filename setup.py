#!/usr/bin/env python

from setuptools import setup

setup(name='Flootty',
      version='0.18',
      description='Floobits collaborative terminal',
      author='Floobits',
      author_email='info@floobits.com',
      url='https://floobits.com/',
      license="Apache2",
      py_modules=['flootty'],
      package_data={
      '': ['README.md']
      },
      entry_points={
      'console_scripts': [
          'flootty = flootty:main',
      ]},
      classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: Apache Software License',
      'Topic :: Terminals',
      'Topic :: Utilities',
      ])
