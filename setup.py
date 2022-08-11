import level
from setuptools import setup, find_packages

setup(
    name='Level',
    version=level.__version__,
    packages=find_packages(),
    url='www.golevel.org',
    license='Copyright (c) 2022 Warp Dynamics Limited. All rights reserved.',
    author='Michal Wojcik',
    author_email='michal.s.wojcik@gmail.com',
    description='',
    scripts=['scripts/level']
)
