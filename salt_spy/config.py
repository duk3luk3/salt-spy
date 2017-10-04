import os

class SpyConfig:
    def __init__(self, **kwargs):
        object.__setattr__(self, '_defaults', kwargs)

    def __getattr__(self, name):
        return os.environ.get('SALTSPY_' + name, self._defaults.get(name))

    def __setattr__(self, name, value):
        self._defaults[name] = value

config = SpyConfig(
    LOGFILE='/var/log/salt-ssh.log',
    DB='/srv/salt-spy/db.sqlite'
)

