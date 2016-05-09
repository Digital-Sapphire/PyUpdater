[![](https://badge.fury.io/py/PyUpdater.svg)](http://badge.fury.io/py/PyUpdater)
[![Build Status](https://travis-ci.org/JMSwag/PyUpdater.svg?branch=master)](https://travis-ci.org/JMSwag/PyUpdater)
[![Build status](https://ci.appveyor.com/api/projects/status/xb85x8ay34rwldui/branch/master?svg=true)](https://ci.appveyor.com/project/JMSwag/pyupdater/branch/master)
[![](https://requires.io/github/JMSwag/PyUpdater/requirements.svg?branch=master)](https://requires.io/github/JMSwag/PyUpdater/requirements/?branch=master)
[![Code Health](https://landscape.io/github/JMSwag/PyUpdater/master/landscape.svg?style=flat)](https://landscape.io/github/JMSwag/PyUpdater/master)

# PyUpdater
#####An update framework that enables simple, secure & efficient shipment of app updates.

####[Docs](http://docs.pyupdater.com)
####[Changelog](https://github.com/JMSwag/PyUpdater/blob/master/docs/changelog.md)
####[License](https://github.com/JMSwag/PyUpdater/blob/master/docs/license.md)


##To Install

#####Stable Lite:

    $ pip install -U PyUpdater

#####Stable Full:

    $ pip install -U PyUpdater[all]

#####Dev:

    $ pip install -U https://github.com/JMSwag/PyUpdater/tarball/master

#####Extras: Amazon S3 & SCP upload plugins are available with

    $ pip install -U PyUpdater[s3]

#####or

    $ pip install -U PyUpdater[scp]

#####Patch support (for creating diffs of app updates):

    $ pip install -U PyUpdater[patch]

##Write your own upload plugin
#####Its up to Plugin authors to get credentials from users. Best practice would be to instruct users to set env vars.

    from pyupdater.uploader import BaseUploader


    class MyUploader(BaseUploader):

        name = 'my uploader'
        author = 'JM'

        def init_config(config):
            "Pyupdater will call this function when setting the uploader"
            # config (dict): a dict with settings specific to this plugin

        def set_config(config):
            # config (dict): a dict with settings specific to this plugin

        def upload_file(self, filename):
            "PyUpdater will call this function on every file that needs to be uploaded."
            # filename (str): Absolute path to file to be uploaded



#####In your setup.py

######Example from s3 upload plugin
```
setup(
    provides=['pyupdater.plugins',],
    entry_points={
        'pyupdater.plugins': [
            's3 = s3_plugin:S3Uploader',
            ]
        },
```

####Examples plugins here available
#####[S3 Plugin](https://github.com/JMSwag/PyUpdater-S3-Plugin "S3 Plugin")
#####[SCP Plugin](https://github.com/JMSwag/PyUpdater-SCP-Plugin "SCP Plugin")

## Supported Update Archive Formats
##### Zip for Windows and GZip for Mac & Linux. Decision based on patch size.

#### Archive Patch Tests:
| Format | Source | Output | Patch |
| ------ | ------ | ------ | ----- |
 7z | 6.5mb | 6.8mb |  6.8mb
bz2 | 6.6mb | 6.8mb | 6.9mb
zip | 6.5mb | 6.8mb | 3.2mb
gz | 6.5mb | 6.8mb | 3.2mb
