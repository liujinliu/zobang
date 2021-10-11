# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

from zobang.version import __version__

package = 'zobang'
version = __version__


setup(
    name=package,
    version=version,
    description='a simple gobang game',
    url='',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'zobang.start=zobang.cmd:game_start'
        ],
    },
)
