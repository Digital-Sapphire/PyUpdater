#Welcome to PyUpdater


##What is PyUpdater?

An AutoUpdate library and toolkit that enables simple, secure & efficient shipment of app updates.

This project would not be possible without [Pyinstaller](https://github.com/pyinstaller/pyinstaller).
## Status

[![](https://badge.fury.io/py/PyUpdater.svg)](http://badge.fury.io/py/PyUpdater)
[![Build Status](https://travis-ci.org/JMSwag/PyUpdater.svg?branch=master)](https://travis-ci.org/JMSwag/PyUpdater)
[![Build status](https://ci.appveyor.com/api/projects/status/6kex9r8i2625pw9u/branch/master?svg=true)](https://ci.appveyor.com/project/JMSwag/pyupdater/branch/master)
[![](https://requires.io/github/JMSwag/PyUpdater/requirements.svg?branch=master)](https://requires.io/github/JMSwag/PyUpdater/requirements/?branch=master)
[![codecov](https://codecov.io/gh/JMSwag/PyUpdater/branch/master/graph/badge.svg)](https://codecov.io/gh/JMSwag/PyUpdater)

##Features

- Easy Setup
- Basic Auth support
- Secured with EdDSA
- Cryptographically secure off line update
- Release channels
- Automatic patch update support
- Intelligent update workflow
- Asynchronous downloads
- Update versioned external assets
- Dual key verification
    - An offline private key signs an application specific key pair.
    - The application specific key pair is used to sign and verify update meta data.
    - The client is shipped with the offline public key to bootstrap the verification process.
- Download progress callback
- Uploading to the cloud handled by plugins.
    - S3 and SCP plugins available
