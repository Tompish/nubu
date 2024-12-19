import os
import tomllib


class Config:

    defaultConf = """
[project]
branches = [ "develop", "acceptance", "main" ]

[project.MysteryOfAton]
branches = [ "fab", "hawt", "glory" ]
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

        with open(confFile, 'rb') as f:
            self.config = tomllib.load(f)['project']

    def check_existing_conf(self, paths):
        """check if a config exists in possible paths.
        Returns first match"""

        for path in paths:
            if os.path.isfile(path+"/nubu.conf"):
                return path+"/nubu.conf"
        else:
            return None

    def get_setting(self, name: str, project: str = '') -> any | None:
        if project in self.config and name in self.config:
            return self.config[project][name]
        elif name in self.config:
            return self.config[name]
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
