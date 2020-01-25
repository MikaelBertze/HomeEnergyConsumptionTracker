try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Home Energy Consumption Web Service',
    'author': 'Mikael Bertze',
    'url': 'http://mikael.bertze.se',
    'download_url': 'https://github.com/MikaelBertze/HomeEnergyConsumptionTracker/webservice',
    'author_email': 'mikael@bertze.com',
    'version': '0.1',
    'install_requires': ['numpy', 'bottle', 'scipy'],
    'packages': [],
    'scripts': [],
    'name': 'HomeEnergyConsumptionTracker_WebService',
    'license': ''
}

setup(**config)
