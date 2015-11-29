
import json

def getSettings(fileName, app):
    """Get Settind - json based settings handler"""

    json_data=open(fileName)
    settings = json.load(json_data)
    json_data.close()
    return settings[app]