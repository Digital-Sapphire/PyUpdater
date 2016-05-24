#Welcome to PyUpdater


####What is PyUpdater?

In its simplest form PyUpdater is a collection of utilities, when used together, makes its super simple to add auto-update functionality to your app. Support for patch updates are included out of the box :)

## Status

[![](https://badge.fury.io/py/PyUpdater.svg)](http://badge.fury.io/py/PyUpdater)
[![Build Status](https://travis-ci.org/JMSwag/PyUpdater.svg?branch=master)](https://travis-ci.org/JMSwag/PyUpdater)
[![Build status](https://ci.appveyor.com/api/projects/status/6kex9r8i2625pw9u?svg=true)](https://ci.appveyor.com/project/JMSwag/pyupdater)
[![](https://requires.io/github/JMSwag/PyUpdater/requirements.svg?branch=master)](https://requires.io/github/JMSwag/PyUpdater/requirements/?branch=master)
<!-- [![Code Health](https://landscape.io/github/JMSwag/PyUpdater/master/landscape.svg?style=flat)](https://landscape.io/github/JMSwag/PyUpdater/master) -->

####A high level break down of the framework consists of 3 parts.

#####Client:
Is the module you import into your app that provides the update functionality.

#####Core:
Consists of the KeyHandler, PackageHandler & Uploader. Use at your own risk. It's really not that bad though.

#####CLI:
Uses core as execution engine. More then likely what you'll be interacting with.

####Features

- Easy Setup
- Secured with EdDSA
- Secure off line update
- Release channels
- Automatic Binary creation/patching
- Smart patch updates
    - This method is only applied if the total size of patches are less than a full update and the user is less than 4 patches behind.
- Asynchronous downloads
- Update your application's artifacts
- Dual key verification
    - If the repository key is compromised it is very easy to create a new one.
- Get download progress with progress hooks a.k.a. callbacks
    - Great for GUI applications.
    - Super easy setup
- Upload system based on a plugin architecture
    - Anyone can create a plugin
    - Plugins are enabled on installation
    - Plugins can optionally get config info from the user
    - Auto save config info
    - Configs are separated from each other by namespace.
    - Plugins will have config info auto loaded before upload
- I really feel like I'm missing something else
