#Work Flow

###Step 1 - Create Keypack
####Create a keypack on an air-gapped computer for best security. You'll be asked for your applications name. It's important that you use the same name when creating a new keypack for the same application. If you don't your updates will fail.
```
$ pyupdater keys -c
```

###Step 2 - Copy Keypack
####Copy the keypack to the development computer & place in the root of the code repository.

###Step 3 - Init Repo
####Now we need to initialize the code repository. You'll be asked a few questions about your application then 2 directories & a config file will be created. The first directory is pyu-data which is used when creating archives, creating patches & housing files before upload. The other is a hidden directory for repo configuration.
```
$ pyupdater init
```

###Step 4 - Import Keypack
####It's time to import our keypack. Make sure it's in the root or the code repository. After you've successfully imported the keypack it's safe to delete.
```
$ pyupdater keys -i
```

###Step 5 - Integrate PyUpdater
####Now we need to add a couple of imports & constants to our main script. You'll also see an example of using the client to update the application & it's artifacts. In simple apps I develop I usually place all client initializing, update checking, downloading & restarting in a function named upgrade(). I then call upgrade before the main function.
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

###Step 6 - Build
####Now let's build our app. You have two options when building. You can specify a spec file or you main script. PyUpdater will use the name set during repo initialization as the final application name.

#####If you go the spec file route:
```
# First create the spec file
$ pyupdater make-spec -w --app-version=1.0.0 main.py

# Then build it
$ pyupdater build --app-version=1.0.0 main.spec
```

#####If you just want to build the script:
```
$ pyupdater build --app-version=1.0.0 main.py
```

###Step 7 - Create patches
####Time to create binary patches if enabled, add sha256 hashes to version manifest & copy files to deploy folder. You can combine --process with --sign.
```
$ pyupdater pkg --process
```

###Step 8 - Cryptographically Sign
####Now lets sign our version manifest file, gzip our version manifest, gzip keyfile & place in the deploy directory. You can combine --sign with --process
```
$ pyupdater pkg --sign
```

###Step 9 - List Installed Plugins
####Get a list of the plugins you have installed. You probably wont have to run this many times :)
```
# You can install the official plugins with
# pip install pyupdater[s3, scp]
$ pyupdater plugins

s3 by Digital Sapphire
scp by Digital Sapphire

```

###Step 10 - Configure Plugin
####Your plugin may or may not need configuration. If you are not sure then go ahead and check. It won't hurt anything. If nothing happens then the coast is clear. Plugin authors may ask you to set env vars. Please consult their docs. Now off we go.
```
$ pyupdater settings --plugin s3
```

###Step 11 - Upload
####We've made it. Time to upload our updates, patches & metadata. On the first run you will not have any patches. There's no src files yet. It'll happen on the next build.
```
$ pyupdater upload --service s3
```
