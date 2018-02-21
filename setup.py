#!/usr/bin/env python

from setuptools import setup
import fnmatch
import os

# Find all the python modules
modules = []
matches = []
for root, dirnames, filenames in os.walk('tuxemon'):
    for filename in fnmatch.filter(filenames, '__init__.py'):
        matches.append(os.path.join(root, filename))

for match in matches:
    match = match.replace(os.sep+"__init__.py", "")
    match = match.replace(os.sep, ".")
    modules.append(match)

# Get the version from the README file.
f = open("README.md", "r")
VERSION = f.readline().split(" ")[-1].replace("\n", "")
f.close()

# Configure the setuptools
setup(name='Tuxemon',
      version=VERSION,
      description='Open source monster-fighting RPG',
      author='William Edwards',
      author_email='shadowapex@gmail.com',
      url='https://www.tuxemon.org',
      include_package_data=True,
      packages=modules,
      license="GPLv3",
      long_description='https://github.com/Tuxemon/Tuxemon',
      entry_points={
          'gui_scripts': [
              'tuxemon = tuxemon.__main__:main'
          ]
      },
      classifiers=[
          "Intended Audience :: End Users/Desktop",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Topic :: Games/Entertainment",
          "Topic :: Games/Entertainment :: Role-Playing",
      ]
      )