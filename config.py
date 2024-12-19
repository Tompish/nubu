import os
import tomllib


class Config:

    defaultConf = """
[project]
stagebranches = [ develop, acceptance, main ]

[project.MysteryOfAton]
stagedbranched = [ fab, hawt, glory ]
    """

    def __init__(self):
        self.conf_path = ''
        self.config = ''

    def valid_config_paths(self):
        """Searches XDG_CONFIG_HOME and returns a list of ranked preferences"""

        paths = []
        if os.environ.get('XDG_CONFIG_HOME'):
            paths.append(os.environ['XDG_CONFIG_HOME'])
        paths.append(os.path.expanduser("~/.config"))
        return paths

    def write_config(self, confFile, text):
        """Writes TOML-text to a given configFile"""

        with open(confFile, 'w') as f:
            f.write(self.defaultConf)

    def read_config(self, confFile):
        """Reads config TOML file and saves it to config.config"""

        with open(confFile) as f:
            self.config = tomllib.loads(f)

    def check_existing_conf(self, paths):
        """check if a config exists in possible paths.
        Returns first match"""

        for path in paths:
            if os.path.isfile(path+"/nubu.conf"):
                return path+"/nubu.conf"
        else:
            return None

    def init_config(self):
        """Initializes config by searching for config
        and loading it into memory"""

        paths = self.valid_config_paths()
        self.conf_path = self.check_existing_conf(paths)
        if not self.conf_path:
            self.conf_path = paths[0]+"/nubu.conf"
            self.write_config(self.conf_path, self.defaultConf)
        else:
            self.read_config(self.conf_path)
        print(self.config)
