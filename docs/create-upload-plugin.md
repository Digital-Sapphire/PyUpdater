# Create Upload Plugins

- PyUpdater finds plugins by setuptools entry points.
- Base class provides helper methods to get and set configuration information.

## Simple Example
my_uploader.py
```

from pyupdater.core.uploader import BaseUploader


class MyUploader(BaseUploader):

    name = 'my uploader'
    author = 'Jane Doe'

    def init_config(self, config):
        self.server_url = config["server_url"]

    def set_config(self, config):
        server_name = self.get_answer("Please enter server name\n--> ")
        config["server_url"] = server_name

    def upload_file(self, filename):
        # Make the magic happen
        files = {'file': open(filename, 'rb')}
        r = request.post(self.server_url, files=files)

```


setup.py
```
setup(
    provides=['pyupdater.plugins',],
    entry_points={
        'pyupdater.plugins': [
            'my_uploader = my_uploader:MyUploader',
            ]
        },
```

## Plugin Settings
Plugin authors have 2 ways of getting and setting config information.

The first way would be to request the information from the user. In your plugin you'd do something like this. 
```
# Saves the config to disk.
def set_config(self, config):
    server_name = self.get_answer("Please enter server name\n--> ")
    config["server_url"] = server_name


# Will be called after the class is initialized.
def init_config(self, config):
    self.server_url = config["server_url"]

```

The second way would be env var.

## Examples plugins
[S3 Plugin](https://github.com/Digital-Sapphire/PyUpdater-S3-Plugin)

[SCP Plugin](https://github.com/Digital-Sapphire/PyUpdater-SCP-Plugin)


