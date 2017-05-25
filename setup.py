from setuptools import setup, find_packages

version = '0.1.7'

REQUIREMENTS = [
    'requests',
    'bs4',
    'six'
]

setup(
    name='incapsula-cracker-py3',
    version=version,
    packages=['incapsula'],
    url='https://github.com/ziplokk1/incapsula-cracker-py3',
    license='LICENSE.txt',
    author='Mark Sanders',
    author_email='sdscdeveloper@gmail.com',
    install_requires=REQUIREMENTS,
    description='A way to bypass incapsula robot checks when using requests.',
    include_package_data=True
)
