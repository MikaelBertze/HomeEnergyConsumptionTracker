try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Home Energy Consumption Tracker Sensors',
    'author': 'Mikael Bertze',
    'url': 'http://mikael.bertze.se',
    'download_url': 'https://github.com/MikaelBertze/HomeEnergyConsumptionTrackeri/homesensors',
    'author_email': 'mikael@bertze.com',
    'version': '0.1',
    'install_requires': ['requests'],
    'packages': ['homesensors'],
    'scripts': [],
    'name': 'HomeEnergyConsumptionTrackerSensors',
    'license' : ''
}

setup(**config)
