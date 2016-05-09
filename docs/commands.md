#Commands

######* Note: All commands must be ran from root or repository.
###Keys
```
usage: pyupdater keys [-h] [-i] [-c] [-y]

optional arguments:
  -h, --help    show this help message and exit
  -i, --import  Imports a keypack from the current working directory
  -c, --create  Creates keypack. Should only be used on your off-line machine
  -y, --yes     Will run command without conformation prompt
```

#####Description
######The keys command is used to create & import keypack files. It's advised to create keypacks on an off-line computer. Keypack files contains keys to cryptographically sign meta-data files used by pyupdater. Keys can be created and imported as many times as needed. Usually only needed when dev machine has been compromised.

#####Example
```
# Create
$ pyupdater keys --create

# Once you initialized your repo & copied the keypack to the root of the repo.
$ pyupdater keys --import
```

###Init
```
usage: pyupdater init [-h]

optional arguments:
  -h, --help            show this help message and exit
```

#####Description
######Initialize a repo for use with PyUpdater. You'll be asked a few question about your application. Once complete a config directory, a data directory & a client_config.py file will be created. It's safe to delete files in the pyu-data directory as needed. Anytime you update your settings a new client_config.py file will be created.

#####Example
```
$ pyupdater init
```


###Build
```bash
usage: pyupdater build [opts] [app.py|app.spec]

optional arguments:
  -h, --help            show this help message and exit
  --clean               Clean build. Bypass the cache
  --app-version APP_VERSION
  -k, --keep            Will not delete executable after archiving
```

#####Description
######The build command wraps pyinstaller to create the final executable. All options are passed to pyinstaller. Once built the executable is archived, in a pyupdater compatible formate, and place in the pyu-data/new directory. If you supply a version number with an alpha or beta tag, when processed this binary will be placed on the respective release channel. Example: 1.0.1beta2

#####Example
```
# Build from python script
$ pyupdater build -F --app-version 1.0 app.py
# Build from spec file
$ pyupdater build --app-version 1.2 app.spec
```


###Archive
```
usage: pyupdater archive [opts] filename

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           Name used when renaming binary before archiving.
  --target-name TARGET_NAME
                        Name of file to be archived
  --version VERSION     Version of file
  -k, --keep            Will not delete source file after archiving
```

#####Description
######The archive command archives the file to be updated in a PyUpdater compatible format. The file must be in the new directory.

#####Example
```
# When you have multiple binaries with the same name even on different platforms.
$ pyupdater archive --name 'ffmpgeg' --target 'ffmpeg-nix64' --version 2.2.4
$ pyupdater archive --name ffmpeg --target ffmpeg-mac --version 2.1
```

###Pkg
```
usage: pyupdater pkg [-h] [-p] [-s]

optional arguments:
  -h, --help         show this help message and exit
  -p, -P, --process  Adds update metadata to version file & moves files from
                     the new to deploy directory.
  -s, -S, --sign     Sign version file
```

#####Description
######The package command is used to process packages, creates patches if possible and process them & update package meta-data. During processing we collect hashes, file size, version & platform info. Once done archives and patches if any are placed in the deploy directory. The sign command, signs the package meta-data, archives the meta-data & places the meta-data archive in the deploy directory.

#####Example
```
# Used to process packages. Usually ran after build or archive command
$ pyupdater pkg -p

# Used to sign meta-data. Can be used anytime.
$ pyupdater pkg -S
```

###Plugins
```
usage: pyupdater plugins [-h]

optional arguments:

  -h, --help        shows this help message and exit
```

#####Description
######The plugins command shows a list of installed plugins & authors name.

#####Example
```
$ pyupdater plugins

s3 by Digital Sapphire
scp by Digital Sapphire

```

###Upload
```
usage: pyupdater upload [-h] [-s SERVICE]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVICE, --service SERVICE
                        Where updates are stored
```

#####Description
######Will upload all data in the deploy folder to the desired remote location. The uploader has a plugin interface. Check the installation page for links to core plugins. Plugins are activated by installation.

#####Example
```
# Upload to Amazon S3
$ pyupdater upload --service s3

# Upload to remote server over ssh
$ pyupdater upload --service scp
```

###Settings
```
usage: pyupdater settings [-h] [--company] [--urls] [--patches] [--scp] [--s3]

optional arguments:
  -h, --help  show this help message and exit
  --company   Change company name
  --urls      Change update urls
  --patches   Changed patch support
  --plugin    Set/Change settings for named plugin
```

#####Description
######To update repo settings pass each flag you'd like to update.

#####Example
```
$ pyupdater settings --company
```

###Help
```
usage: pyupdater

positional arguments:
  {archive,build,clean,collect-debug-info,init,keys,make-spec,pkg,settings,update,upload,version}
                        commands
    archive             Archives external file which needs updating. Can be
                        binary, library, anything really.
    build               compiles script or spec file
    clean               * WARNING * removes all traces of pyupdater for the current repo
    collect-debug-info  Upload debug logs to github gist and return url.
    init                initializes a src directory
    keys                Manage signing keys
    make-spec           Creates spec file
    pkg                 Manages creation of file meta-data & signing
    settings            Updated config settings
    update              Updates repo. Should be ran after you update pyupdater
    upload              Uploads files
    version             Show version

optional arguments:
  -h, --help            show this help message and exit
```


###Demos
#####Example of using the client within your app can be found in the demos folder.

###Limitations

#####* No onedir support