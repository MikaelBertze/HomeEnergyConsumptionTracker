try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Home Energy Consumption Tracker',
    'author': 'Mikael Bertze',
    'url': 'http://mikael.bertze.se',
    'download_url': 'https://github.com/MikaelBertze/HomeEnergyConsumptionTracker',
    'author_email': 'mikael@bertze.com',
    'version': '0.1',
    'install_requires': [],
    'packages': ['Sensors'],
    'scripts': [],
    'name': 'HomeEnergyConsumptionTracker',
    'license' : ''
}

setup(**config)
