# Installation
PyUpdater depends on a few external libraries:
[appdirs](https://pypi.python.org/pypi/appdirs/), [bsdiff4](https://github.com/ilanschnell/bsdiff4), [certifi](https://pypi.python.org/pypi/certifi), [dsdev-utils](https://pypi.python.org/pypi/dsdev-utils), [pyinstaller](https://github.com/pyinstaller/pyinstaller), [pynacl](https://pypi.org/project/PyNaCl/), [stevedore](https://pypi.python.org/pypi/stevedore) & [urllib3](https://pypi.python.org/pypi/urllib3).

#### Install Stable version

    $ pip install --upgrade PyUpdater


#### Install w/ upload plugins

    $ pip install --upgrade PyUpdater[s3]

    $ pip install --upgrade PyUpdater[scp]


#### For complete install

    $ pip install --upgrade PyUpdater[all]


Be sure to check the plugins docs for setup & configuration options.

[PyUpdater-S3-Plugin](https://github.com/Digital-Sapphire/pyupdater-s3-plugin)

[PyUpdater-SCP-Plugin](https://github.com/Digital-Sapphire/pyupdater-scp-plugin)


#### Install Development version
We are not responsible for broken things but please report your findings ;)

    $ pip install --upgrade git+https://github.com/Digital-Sapphire/PyUpdater.git@master
