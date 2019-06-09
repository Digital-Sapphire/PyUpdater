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
####See Usage | Client


###Step 6 - Make Spec
####Is your app more of the demanding type? If so, your spec file must be based on  a PyUpdater generated spec file. You can easily generate one using the example below. If you do not need a custom spec file skip to the next step. Please see the Danger Zone section on spec files.
```
$ pyupdater make-spec -w main.py

# or

$ pyupdater make-spec -F -w main.py

# To show pyinstaller build info use --pyinstaller-log-info
```

###Step 7 - Build
####Now let's build our app. You have two options when building. You can specify a spec file or a main script. Please see the Danger Zone section on version numbers.

```
# Build from a spec file.
$ pyupdater build --app-version=1.0.0 main.spec

# Build from a script.
$ pyupdater build --app-version=1.0.0 main.py

# To show pyinstaller build info use --pyinstaller-log-info
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

# For CI/CD
$ pyupdater pkg --sign --slit-version
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
