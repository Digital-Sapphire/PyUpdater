# Usage | CLI

### Step 1 - Create Keypack

Create a keypack on an air-gapped computer, not your dev machine, for best security. You'll be asked for the name of the application. It's important that you use the same name when creating a new keypack for the same application. If you don't your application will not be able to verify update meta-data and will not auto-update!

```
$ pyupdater keys -c
```

### Step 2 - Copy Keypack

Copy the keypack to the dev machine & place in the root of the code repository.

```bash
$ scp dev-machine:keypack.pyu .
```

### Step 3 - Init Repo

In the root of your repo run the init command. You'll be asked a few questions about your application then 2 directories & a config file will be created. The first directory is pyu-data which is used as a working directory for PyUpdater. The other is a hidden directory for repository configuration and data files.

```
$ pyupdater init
```

### Step 4 - Import Keypack

Make sure the keypack file is in the root the repo. After you've successfully imported the keypack it's safe to delete.

```
$ pyupdater keys -i
```

### Step 5 - Integrate PyUpdater

[See Usage | Client](usage-client.md)

### Step 6 - Make Spec

Is your app more of the demanding type? Generate your spec file with PyUpdater then make edits as necessary. If you do not need a custom spec file skip to the next step. Please see the spec-file section in the [Danger Zone](danger-zone.md).

```
$ pyupdater make-spec -w main.py

# or

$ pyupdater make-spec -F -w main.py

# To show pyinstaller build info use --pyinstaller-log-info
```

### Step 7 - Build

You have two options when building. You can specify a spec file or a main script. Please see the version numbers section in the [Danger Zone](danger-zone.md).

```
# Build from a spec file.
$ pyupdater build --app-version=1.0.0 main.spec

# Build from a script.
$ pyupdater build --app-version=1.0.0 main.py

# To show pyinstaller build info use --pyinstaller-log-info
```

### Step 8 - Create patches

Gets sha256 hashes, file sizes, adds meta-data to version manifest and copies files to deploy folder. If a source files is available, patches will also be created. You can combine --process with --sign.

```
$ pyupdater pkg --process
```

### Step 9 - Cryptographically Sign

Now lets sign & gzip our version manifest, gzip our keyfile & place both in the deploy directory. Note that the signing process works without any user intervention. You can combine --sign with --process

```
$ pyupdater pkg --sign

# For CI/CD
$ pyupdater pkg --sign --split-version
```

### Step 10 - List Installed Plugins

Get a list of the plugins you have installed. You probably wont have to run this many times :)

```
# You can install the official plugins with
# pip install pyupdater[s3, scp]
$ pyupdater plugins

s3 by Digital Sapphire
scp by Digital Sapphire

```

### Step 11 - Configure Plugin

Your plugin may or may not need configuration. If you are not sure then please check the documentation for that plugin.

```
$ pyupdater settings --plugin s3
```

### Step 12 - Upload

We've made it. Time to upload our updates, patches & metadata. You won't have any patches to upload on the first run. Don't worry they'll be there next time.

```
$ pyupdater upload --service s3
```

### Debugging Issues

Sometimes issues arise like misconfigured upload URLs or keys. To debug issues that involve PyUpdater, create the file `pyu.log` in the root of your app.

PyUpdater will log debug statements to this file and hopefully provide you with information to assist with your debugging.
