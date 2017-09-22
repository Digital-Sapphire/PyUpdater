#Create Upload Plugins

- PyUpdater finds plugins by setuptools entry points.
- Base class provides helper methods to get and set configuration information.

##Simple Example
####my_uploader.py
```python

from pyupdater.uploader import BaseUploader


class MyUploader(BaseUploader):

    name = 'my uploader'
    author = 'Jane Doe'

    def init_config(self, config):
        "Pyupdater will call this function when setting the uploader"
        # config (dict): a dict with settings specific to this plugin

    def set_config(self, config):
        "This method will be called when a user selects your plugin from the settings flag"
        # config (dict): a dict with settings specific to this plugin

    def upload_file(self, filename):
        "PyUpdater will call this function on every file that needs to be uploaded."
        # filename (str): Absolute path to the file
```


####In your setup.py
```
setup(
    provides=['pyupdater.plugins',],
    entry_points={
        'pyupdater.plugins': [
            'my_uploader = my_uploader:MyUploader',
            ]
        },
```

##Plugin Settings
Plugin authors have 2 ways of getting and setting config information.

The first way would be to request the information from the user. In your plugin you'd do something like this. 
```python
# Saves the config to disk.
def set_config(self, config):
    
    server_name = self.get_answer('Please enter the server name\n--> ')
    
    config["server_name"] = server_name

# Will be called after the class is initialized.
def init_config(self, config):
    self.server_name = config["server_name"]
    
```

The second way would be env var.

##Examples plugins
###[S3 Plugin](https://github.com/JMSwag/PyUpdater-S3-Plugin "S3 Plugin")
###[SCP Plugin](https://github.com/JMSwag/PyUpdater-SCP-Plugin "SCP Plugin")