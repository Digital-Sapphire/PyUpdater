[![](https://badge.fury.io/py/PyUpdater.svg)](http://badge.fury.io/py/PyUpdater)
[![Build Status](https://travis-ci.org/JMSwag/PyUpdater.svg?branch=master)](https://travis-ci.org/JMSwag/PyUpdater)
[![Build status](https://ci.appveyor.com/api/projects/status/xb85x8ay34rwldui/branch/master?svg=true)](https://ci.appveyor.com/project/JMSwag/pyupdater/branch/master)
[![](https://requires.io/github/JMSwag/PyUpdater/requirements.svg?branch=master)](https://requires.io/github/JMSwag/PyUpdater/requirements/?branch=master)
[![Code Health](https://landscape.io/github/JMSwag/PyUpdater/master/landscape.svg?style=flat)](https://landscape.io/github/JMSwag/PyUpdater/master)

# PyUpdater
#####An update framework that enables simple, secure & efficient shipment of app updates.

####[License](https://github.com/JMSwag/PyUpdater/blob/master/docs/license.md)
####[Full changelog](https://github.com/JMSwag/PyUpdater/blob/master/docs/changelog.md)


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


##Simple Usage:

######To add PyUpdater to your applications all you need are a couple of imports & constants. Below is a snippet of code that'll better explan.

```
# Imports
from client_config import ClientConfig
from pyupdater.client import Client

# Constants
APP_NAME = 'Acme'
APP_VERSION = 1.0

client = Client(ClientConfig(), refresh=True)

# Returns an update object
update = client.update_check(APP_NAME, APP_VERSION)

# Optionally you can use release channels
# Channel options are stable, beta & alpha
# Note: Patches are only created & applied on the stable channel
app_update = client.update_check(APP_NAME, APP_VERSION, channel='stable')

# Use the update object to download an update & restart the app
if app_update is not None:
    downloaded = app_update.download()
    if downloaded is True:
        app_update.extract_restart()

```




#####To compile & package your script

    $ pyupdater build -F --app-version=0.1.0 example_app.py


#####To update & sign your version file.

    $ pyupdater pkg --process

    $ pyupdater pkg --sign

#####Upload your updates to Amazon S3

    $ pyupdater upload --service s3


#####For help & extra commands

    $ pyupdater -h
    $ pyupdater command -h


###[Complete Docs](http://docs.pyupdater.com)


##Write your own upload plugin
#####Its up to Plugin authors to get credentials from users. Best practice would be to instruct users to set env vars.

    from pyupdater.uploader import BaseUploader


    class MyUploader(BaseUploader):

        def __init__(self):
            super(MyUplaoder, self).__init__()

        def init(**kwargs):
            # files (list): List of files to upload
            #
            # The following items are not guaranteed & may be None
            #
            # object_bucket (str): AWS S3/Dream Objects/Google Storage Bucket
            #
            # ssh_remote_dir (str): Full path on remote machine to place updates
            #
            # ssh_username (str): user account on remote server for uploads
            #
            # ssh_host (str): Remote host to connect to for server uploads


        def connect(self):
            # Connect to service here

        def upload_file(self, filename):
            # Upload file here
            # PyUpdater will call this function on every file that needs to be uploaded


#####In your setup.py

######Example from s3 upload plugin

    entry_points={
        'pyupdater.plugins.uploaders': [
            's3 = s3_plugin:S3Uploader',
        ]


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
