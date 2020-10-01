# Commands

###### * Note: All commands must be run from the root of the repository.

### Archive
```
usage: pyupdater archive [opts] filename

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           Name used when renaming binary before archiving.
  --version VERSION     Version of file
  -k, --keep            Will not delete source file after archiving
```

Description:

The archive command will archive an external asset used by your application which will allow updating of the asset. An example of this would be if your application depended on ffmpeg but you did not want to bundle ffmpeg within your app. See [Usage | CLI | Assets](usage-cli-asset.md) & [Usage | Client | Assets](usage-client-asset.md) for more info.

Example:
```
$ pyupdater archive --name ffmpeg --version 2.1.4

$ pyupdater archive --name ffmpeg --version 2.2
```


### Build
```
usage: pyupdater build [opts]<script>

optional arguments:
  -h, --help            show this help message and exit
  --archive-format {zip,gztar,bztar,default}
  --clean               Clean build. Bypass the cache
  --app-version APP_VERSION
  -k, --keep            Will not delete executable after archiving
  --pyinstaller-log-info
                        Prints PyInstaller execution info to consoleconsole
```

Description:

The build command wraps pyinstaller to create the final executable. All options are passed to pyinstaller. Once built the executable is archived, in a pyupdater compatible format, and placed in the pyu-data/new directory. If you supply a version number with an alpha or beta tag, when processed this binary will be placed on the respective release channel. If enabled, patches will also be created and placed on the respective release channel.

Example:
```
# Build from python script
$ pyupdater build -F --app-version 1.0 app.py

# Build from spec file (see Make Spec on how to create spec files)
$ pyupdater build --app-version 1.2 app.spec

# Beta channel
$ pyupdater build --app-version 1.2beta2
```


### Clean
```
usage: pyupdater clean [-h] [-y]

optional arguments:
  -h, --help  show this help message and exit
  -y, --yes   Confirms removal of pyu-data & .pyupdater folder
```

Description:

Removes all traces of PyUpdater from the current repository.

Example:
```
$ pyupdater clean
```


### Collect Debug Info
```
usage: pyupdater collect-debug-info [-h]

optional arguments:
  -h, --help  show this help message and exit
```

Description:

Uploads debug logs, from pyupdater's CLI, to a private gist.

Example:
```
$ pyupdater collect-debug-info
```


### Init
```
usage: pyupdater init [-h]

optional arguments:
  -h, --help            show this help message and exit
```

Description:

Initialize a repo for use with PyUpdater. You'll be asked a few question about your application. Once complete a config directory, a data directory & a client_config.py file will be created. It's safe to delete files in the pyu-data directory as needed. Anytime you update your settings a new client_config.py file will be created.

Example:
```
$ pyupdater init
```


### Keys
```
usage: pyupdater keys [-h] [-i] [-c] [-y]

optional arguments:
  -h, --help    show this help message and exit
  -i, --import  Imports a keypack from the current working directory
  -c, --create  Creates keypack. Should only be used on your off-line machine
  -y, --yes     Will run command without conformation prompt
```

Description:

The keys command is used to create & import keypack files. It's advised to create keypacks on an off-line computer. Keypack files contains keys to cryptographically sign meta-data files used by pyupdater. Keys can be created and imported as many times as needed. Usually only needed when a development machine has been compromised.

Example:
```
# Create
$ pyupdater keys --create

# Once you initialized your repo & copied the keypack to the root of the repo.
$ pyupdater keys --import
```


### Make Spec
```
usage: pyupdater make-spec <script> [opts]

optional arguments:
  -h, --help            show this help message and exit
  --pyinstaller-log-info
                        Prints PyInstaller execution info to console
```

Description:

Used to create a pyupdater compatible spec file

Example:
```
$ pyupdater make-spec app.py
```


### Pkg
```
usage: pyupdater pkg [-h] [-p] [-s] [--split-version] [-v]

optional arguments:
  -h, --help         show this help message and exit
  -p, -P, --process  Adds update metadata to version file & moves files from
                     the new to deploy directory.
  -s, -S, --sign     Sign version file
  --split-version    Creates a version manifest for the current platform only. For CI/CD
  -v, --verbose      More output messages

```

Description:

The process flag is used to process packages, creates patches if possible and process them & update package meta-data. During processing we collect hashes, file size, version & platform info. Once done archives and patches, if any, are placed in the deploy directory. The sign flag signs the package meta-data, archives the meta-data & places those assets in the deploy directory.

Example:
```
# Used to process packages. Usually ran after build or archive command
$ pyupdater pkg -p

# Used to sign meta-data. Can be used anytime.
$ pyupdater pkg -S
```

### Plugins
```
usage: pyupdater plugins [-h]

optional arguments:

  -h, --help        shows this help message and exit
```

Description:

The plugins command shows a list of installed upload plugins & authors name.

Example:
```
$ pyupdater plugins

s3 by Digital Sapphire
scp by Digital Sapphire

```


### Settings
```
usage: pyupdater settings [-h] [--company] [--config-path] [--http-timeout]
                          [--max-download-retries] [--patches]
                          [--plugin PLUGIN] [--show-plugin SHOW_PLUGIN]
                          [--urls]

optional arguments:
  -h, --help            show this help message and exit
  --company             Change company name
  --config-path         Path to place your client config. You'll need to
                        import this file to initialize the update process.
  --http-timeout        Settings the timeout, in seconds, for the
                        FileDownloader
  --max-download-retries
                        Set the max number of times to try a download.
  --patches             Changed patch support
  --plugin PLUGIN       Change the named plugin's settings
  --show-plugin SHOW_PLUGIN
                        Show the name plugin's settings
  --urls                Change update urls
```
Description:

Update configuration for the current repository.

Example:
```
$ pyupdater settings --urls

$ pyupdater settings --plugin s3

$ pyupdater settings --company
```


### Upload
```
usage: pyupdater upload [-h] [--keep] [-s SERVICE]

optional arguments:
  -h, --help            show this help message and exit
  --keep                Keep files after upload
  -s SERVICE, --service SERVICE
                        The plugin used for uploads
```

Description:

Uploads all data in the deploy folder to the desired remote location. The uploader has a plugin interface. Check the installation page for links to core plugins. Plugins are activated by installation.

Example:
```
# Upload to Amazon S3
$ pyupdater upload --service s3

# Upload to remote server over ssh
$ pyupdater upload --service scp
```


### Help
```
usage: pyupdater

positional arguments:
  {archive,build,clean,collect-debug-info,init,keys,make-spec,pkg,plugins,settings,upload,version}
                        commands
    archive             Archive an asset which needs updating. Can be another
                        executable, .so, .dll, .img, etc.
    build               Compiles script or spec file
    clean               * WARNING * removes all traces of pyupdater from the
                        current repo
    collect-debug-info  Upload debug logs to github gist and return url.
    init                Initializes a src directory
    keys                Manage signing keys
    make-spec           Creates spec file
    pkg                 Manage creation of file meta-data & signing
    plugins             Shows installed plugins
    settings            Updated config settings
    upload              Uploads files
    version             Show version

optional arguments:
  -h, --help            show this help message and exit
```

Description:

Shows help information

Example:
```
$ pyupdater -h

$ pyupdater {command} -h
```
