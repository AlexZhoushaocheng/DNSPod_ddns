from configparser import ConfigParser

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class ConfigMrg():
    def __init__(self):
        self.conf = ConfigParser()
        self.conf.read('conf.ini')
        
    def get_secret_id(self):
        return self.conf['credential']['secret_id']
    
    def get_secret_key(self):
        return self.conf['credential']['secret_key']