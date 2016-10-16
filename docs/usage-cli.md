#Usage | CLI

###Step 1 - Create Keypack
####Create a keypack on an air-gapped computer for best security. You'll be asked for the name of the application. It's important that you use the same name when creating a new keypack for the same application. If you don't your application will not be able to verify update meta-data and will not auto-update..
```
$ pyupdater keys -c
```

###Step 2 - Copy Keypack
####Copy the keypack to the development computer & place in the root of the code repository.

###Step 3 - Init Repo
####Now we need to initialize the code repository. You'll be asked a few questions about your application then 2 directories & a config file will be created. The first directory is pyu-data which is used as a working directory for PyUpdater. The other is a hidden directory for repository configuration.
```
$ pyupdater init
```

###Step 4 - Import Keypack
####It's time to import our keypack. Make sure the keypack file is in the root of the code repository. After you've successfully imported the keypack it's safe to delete.
```
$ pyupdater keys -i
```

###Step 5 - Integrate PyUpdater
####Now we need to add a couple of imports & constants to our main script. Below you can see an example of using the client to update the application & it's artifacts. In simple apps I develop I usually place all client initializing, update checking, downloading & restarting in a function named upgrade(). I then call upgrade before the main function.
```
# Imports
from client_config import ClientConfig
from pyupdater.client import Client

# Constants
APP_NAME = 'Acme'
APP_VERSION = 1.0

LIB_NAME = 'My external library'
LIB_VERSON = '2.4.1'

# This could potentially cause slow app start up time.
# You could use client = Client(ClientConfig()) and call
# client.refresh() before you check for updates
client = Client(ClientConfig(), refresh=True)

# Returns an update object
update = client.update_check(APP_NAME, APP_VERSION)

# Optionally you can use release channels
# Channel options are stable, beta & alpha
# Note: Patches are only created & applied on the stable channel
app_update = client.update_check(APP_NAME, APP_VERSION, channel='stable')
lib_update = client.update_check(LIB_NAME, LIB_VERSON)

# Use the update object to download an update & restart the app
if app_update is not None:
    downloaded = app_update.download()
    if downloaded is True:
        app_update.extract_restart()

# It's also possible to update an external library, file or anything else needed by your application.
if lib_update is not None:
    downloaded = lib_update.download()
    if downloaded is True:
        # The path to the archive.
        lib_update.abspath
```

###Step 6 - Make Spec
####Is your app more of the demanding type? If so, your spec file must be based on  a PyUpdater generated spec file. You can easily generate one using the example below. If you do not need a custom spec file skip to the next step.
```
$ pyupdater make-spec -w main.py
```

###Step 7 - Build
####Now let's build our app. You have two options when building. You can specify a spec file or a main script.

#####Build from a spec file.
```
$ pyupdater build --app-version=1.0.0 main.spec
```

#####Build from a script.
```
$ pyupdater build --app-version=1.0.0 main.py
```

###Step 8 - Create patches
####Time to create binary patches if enabled, add sha256 hashes to version manifest & copy files to deploy folder. You can combine --process with --sign.
```
$ pyupdater pkg --process
```

###Step 9 - Cryptographically Sign
####Now lets sign & gzip our version manifest, gzip our keyfile & place both in the deploy directory. Note that the signing process works without any user intervention. You can combine --sign with --process
```
$ pyupdater pkg --sign
```

###Step 10 - List Installed Plugins
####Get a list of the plugins you have installed. You probably wont have to run this many times :)
```
# You can install the official plugins with
# pip install pyupdater[s3, scp]
$ pyupdater plugins

s3 by Digital Sapphire
scp by Digital Sapphire

```

###Step 11 - Configure Plugin
####Your plugin may or may not need configuration. If you are not sure then please check the documentation for that plugin.
```
$ pyupdater settings --plugin s3
```

###Step 12 - Upload
####We've made it. Time to upload our updates, patches & metadata. You won't have any patches to upload on the first run. Don't worry they'll be there next time.
```
$ pyupdater upload --service s3
```
