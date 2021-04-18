# Welcome to PyUpdater

If you think PyUpdater is awesome, please give [this issue](https://github.com/vinta/awesome-python/pull/720) an up vote on [awesome-python](https://github.com/vinta/awesome-python).


## What is PyUpdater?

An auto-update library and cli tool that enables simple, secure & efficient shipment of app updates.

This project would not be possible without [Pyinstaller](https://github.com/pyinstaller/pyinstaller).
## Status

[![](https://badge.fury.io/py/PyUpdater.svg)](http://badge.fury.io/py/PyUpdater)
![](https://github.com/Digital-Sapphire/PyUpdater/actions/workflows/main.yaml/badge.svg)
[![codecov](https://codecov.io/gh/Digital-Sapphire/PyUpdater/branch/master/graph/badge.svg)](https://codecov.io/gh/JMSwag/PyUpdater)

## Features

- Easy Setup
- CI/CD Support
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
