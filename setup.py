"""Setuptools Installer."""
from setuptools import setup, find_packages

setup(
    name='yappt',
    version='1.0.0',
    py_modules=['yappt'],
    install_requires=[
        'click',
        'ruamel.yaml',
        'pyfiglet',
        'mistletoe',
    ],
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        yappt=yappt.main:main
    ''',
)
