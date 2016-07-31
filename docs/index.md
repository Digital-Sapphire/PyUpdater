#Welcome to PyUpdater


##What is PyUpdater?

An autoupdate framework for pyinstaller that enables simple, secure & efficient shipment of app updates.

## Status

[![](https://badge.fury.io/py/PyUpdater.svg)](http://badge.fury.io/py/PyUpdater)
[![Build Status](https://travis-ci.org/JMSwag/PyUpdater.svg?branch=master)](https://travis-ci.org/JMSwag/PyUpdater)
[![Build status](https://ci.appveyor.com/api/projects/status/6kex9r8i2625pw9u?svg=true)](https://ci.appveyor.com/project/JMSwag/pyupdater)
[![](https://requires.io/github/JMSwag/PyUpdater/requirements.svg?branch=master)](https://requires.io/github/JMSwag/PyUpdater/requirements/?branch=master)
[![Code Health](https://landscape.io/github/JMSwag/PyUpdater/master/landscape.svg?style=flat)](https://landscape.io/github/JMSwag/PyUpdater/master)
[![Codewake](https://www.codewake.com/badges/ask_question.svg)](https://www.codewake.com/p/pyupdater)
[![Gitter](https://badges.gitter.im/pyupdater/Lobby.svg)](https://gitter.im/pyupdater/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

##Features

- Easy Setup
- Secured with EdDSA
- Secure off line update
- Release channels
- Automatic Binary creation/patching
- Smart patch updates
    - This method is only applied if the total size of patches are less than a full update and the user is less than 4 patches behind.
- Asynchronous downloads
- Update your application's assets
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


##Demos

Example of using the client within your app can be found in the demos folder.

##Limitations

* No Pyinstaller onedir support