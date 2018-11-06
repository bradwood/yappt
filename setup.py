"""Setuptools Installer."""
from setuptools import setup

setup(
    name='yappt',
    version='0.0.1',
    py_modules=['yappt'],
    install_requires=[
        'click',
        'ruamel.yaml',
    ],
    entry_points='''
        [console_scripts]
        yappt=yappt.main:main
    ''',
)
