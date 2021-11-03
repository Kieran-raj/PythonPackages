from setuptools import find_packages, setup

setup(
    name='PythonPackages',
    version='0.0.1',
    description='A python package which contains modules for personal use',
    author='Kieran Rajasansir',
    packages=find_packages(
        include=['expenses_data_upload', 'expenses_data_upload.helpers']),
    install_requires=[
        'pdfplumber',
        'PyMySQL'
    ]

)
