# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='robotframework-fritzhomelibrary',
      version='1.3.0',
      author='Oliver Eickmeyer',
      author_email='oliver.eickmeyer@gmail.com',
      description='Access to AVM Home Automation with Robot Framework',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/oeick/robotframework-fritzhomelibrary',
      keywords='robotframework testing homeautomation fritzbox',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent"
      ],
      install_requires=[
          'robotframework >= 3.1.0',
          'requests >= 2.21.0'
      ],
      packages=['FritzHome'],
      )
