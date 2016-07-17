#Installation
PyUpdater depends on a few external libraries:
[appdirs](https://pypi.python.org/pypi/appdirs/), [bsdiff4](https://github.com/ilanschnell/bsdiff4), [certifi](https://pypi.python.org/pypi/certifi), [cryptography](https://pypi.python.org/pypi/cryptography/)[ed25519](https://pypi.python.org/pypi/ed25519), [jms_utils](https://pypi.python.org/pypi/JMS-Utils), [pyinstaller](https://github.com/pyinstaller/pyinstaller), [requests](https://pypi.python.org/pypi/requests), [six](https://pypi.python.org/pypi/six), [stevedore](https://pypi.python.org/pypi/stevedore) & [urllib3](https://pypi.python.org/pypi/urllib3).

* Note Bsdiff4 is only required to make patches, not to apply them.  These libraries are not documented here.

So how do you get all that on your computer quickly?


####Install Stable version

    $ pip install PyUpdater


####For complete install with aws s3 & scp upload plugins

    $ pip install PyUpdater[all]


####S3 & SCP upload plugins

    $ pip install PyUpdater[s3]

    $ pip install PyUpdater[scp]


#####Be sure to check the plugins docs for setup & configuration options.

[PyUpdater-S3-Plugin](https://github.com/JohnyMoSwag/pyupdater-s3-plugin)

[PyUpdater-SCP-Plugin](https://github.com/JohnyMoSwag/pyupdater-scp-plugin)


####Install Development version
#####We are not responsible for broken things!

    $ pip install -U https://github.com/JohnyMoSwag/PyUpdater/tarball/master