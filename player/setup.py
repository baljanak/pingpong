# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def read_file(filename):
    """Read and return lines"""
    with open(filename) as f:
        return map(lambda x: x.strip(), f.readlines())


scripts = [
    'player = player:main',
]

setup(name='player',
      version='0.0.1',
      url='https://github.com/baljanak-bak/pingpong',
      author='baljanak-bak',
      install_requires=read_file('requirements.txt'),
      author_email='baljanak.bak@gmail.com',
      description='Ping Pong Championship: Player',
      packages=find_packages(),
      include_package_data=True,
      platforms='linux',
      entry_points={
          'console_scripts': scripts,
      },
      zip_safe=True)
