# Changelog

## v4.0 - Master
##### * This version is not yet released and is under active development.

### Added

  - Client
    - Added rename update strategy. Windows Only 
    - Support generic headers and HTTP timeouts

### Updated
  - Core
    - Named logger for pyupdater

### Fixed
  
  - Client
    - Attempt to attach to root logger
    - Using custom downloader
    - Max download retries not set for manifest & key files
    - Content decoding

### Removed

  - Python 2
  - Logging http headers

## v3.1.1 - 2019/06/11

### Fixed

  - Client
    - Patch updates


## v3.1.0 - 2019/06/10

### Added

  - PyUpdater
    - Support for bz2 archive format
    - Support for splitting version manifest by platform
    - Support for servers other than directory listing like Github Releases & Bintray.
    See [Usage | Client | Advanced](usage-client-advanced.md#Use-your-own-file-downloader) and
    [Create Upload Plugins](create-upload-plugin.md)

  - CLI
    - Ability to specify archive format
    - pkg --sign --split-version
      - Used with CI/CD

### Fixed
  - Client
    - Saving the version manifest to disk for offline updates
    - Basic Auth
    - Updating on systems with unicode paths: PY2

### Removed
  - PyUpdater
    - Work around to support generating keys on Windows Python 64bit.
        - python-ed25519 1.5 fixed the issue

## v3.0.1 - 2019/05/05

### Fixed
  
  - CLI
    - Uploading from deploy folder


## v3.0.0 - 2019/05/04

### Added

  - CLI
    - Suppresses pyinstaller build logging by default
      - Enabled with --pyinstaller-log-info

  - Client
    - Ability to elevate privileges on windows
    - Patch support for alpha and beta channels

### Updated

  - Client
    - AppUpdate.download(async=True) is now AppUpdate.download(background=True)
    - LibUpdate.download(async=True) is now LibUpdate.download(background=True)

### Fixed

  - CLI
    - Out of memory error on windows
    - Redundant logging to console
    - Handling symlinks within Mac.app


## v2.5.3 - 2018/03/30

### Fixed

  - Deployment issue


## v2.5.2 - 2018/03/30

### Fixed

  - Client
    - Headers printed to console
    - FileNotFoundError
    - More informative error for progress_hooks containers
    - Update failures on chinese version of windows


## v2.5.1 - 2017/11/24

### Fixed

  - Client
    - Removal of applications other than the one being updated (mac)

### Updated

  - Client
    - Remove old archives in background thread


## v2.5.0 - 2017/09/30

### Added

  - Client
    - Basic Auth
  
  - Docs
    - Helpful Esky migration tips
    
  - PyUpdater
    - Pyinstaller onedir support
  
  - Tests
    - Python 3.6
    
### Updated

  - Docs
    - API
    - Plugin creation
    - Repository Layout

### Removed

  - Docs
    - Gitter Link
  
  - Tests
    - Python 3.3 


## v2.4.1 - 2017/09/18

### Fixed

  - CLI
    - Fix command detection @jameshilliard


## v2.4.0 - 2017/09/17

### Added

  - Client
    - Ability to specify a custom folder for update files. @mayli
  
  - PyUpdater
    - Arm support

### Updated
  
  - Client
    - Faster & more efficient downloads. @mayli
    - Error messages on expected errors

  - Docs
    - Code example
  
  - Libs
    - appdirs 1.4.3
    - urllib3 1.22
    - six 1.11.0

### Fixed

  - CLI
    - Saving config changes when keypack isn't imported.
  
  - PyUpdater
      - Failing test @jameshilliard

### Removed

  - PyUpdater
    - Unused code
    - Flaky tests


## v2.3.2 - 2017/02/04

### Fixed

  - CLI
      - Calling certain commands


## v2.3.1 - 2017/02/04

### Fixed

  - CLI
    - Creating keypack.pyu files for new users


## v2.3.0 - 2017/01/29

### Updated

  - Client
    - Added option to update_check which allows for being less restrictive about looking on the specific channel for updates. The default setting is to only allow from the provided channel.

  - Libs
    - certifi 2016.9.26
    - dsdev-utils 0.9.6
    - urllib3 1.20

### Fixed

  - Client
    - Restart - Linux & Mac
  - CLI
    - MemoryError - Windows Python 3.5 64bit
  - PyUpdater
    - Parsing a pre-release format

### Removed

  - Extra Y/N prompt before keypack creation
  - Unused code


## v2.2.0 - 2016/10/29

### Added

  - Client
    - version attribute on update object is a version string in a human readable format.

  - Docs
    - API

### Updated

  - Docs
    - Usage | CLI
  - Libs
    - dsdev-utils 0.9.2
    - requests 1.18.1

### Fixed

  - Client
    - Remove all files used to auto-update after application update - win
    - Restart GUI applications on Mac & Linux

### Removed

  - Client
    - Writing debug log -- @cbenhagen
    - Unused code


## v2.1.7 - 2016/09/30

### Updated

  - Docs
    - Added note about signing

### Fixed

  - Deploy error

## v2.1.6 - 2016/09/30

### Fixed

 - Deploy script


## v2.1.5 - 2016/09/29

### Added

  - Tests
    - Auto update
    - One dir support - currently disabled
    - pytest-datadir

### Updated

  - Client
    - No longer importing unused functions
  - Docs
    - Page titles
    - Install instructions
  - Libs
    - versioneer 0.17
    - urllib3 1.18
  - Tests
    - To coincide with the refactoring of some modules

### Fixed

  - CLI
    - Writing public key to client config
    - Uploading of debug logs
    - version output -- @cbenhagen


## v2.1.4 - 2016/09/06

### Updated

  - Client
    - Percent complete shows up to 1 decimal
  - Core
    - More efficient deltas. (A small internal app now has a patch size of 2kb, down from 1.4mb.)
  - Docs
    - Add missing commands
  - Libs
    - urllib3 1.17

### Removed

  - CLI
    - requirement of --target-name on archive command
  - Client
    - bsdiff python implementation (slower & no longer used)
  - Core
    - Extended pause after uploading
    - Redundant compatibility code

###Deprecated

  - CLI
    - Unused flags for make-spec command


## v2.1.3 - 2016/08/19

### Added

  - CLI
    - Ability to set max download retries. 1-10
  - Tests
    - Auto update

### Fixed

  - Docs
    - Links on Install page - @LucaBernstein
    - Only log debug
  - Encoding URL's
  - Usage on 64bit linux

### Updated

  - Client
    - Decreased memory usage when downloading data
  - Docs
    - Badges reflect master build status
  - Tests
    - Less output on appveyor

### Removed

  - Docs
    - Obsolete info
  - Redundant code
  - Unused requirements


## v2.1.2 - 2016/08/10

### Added

  - Client
    - Reporting of percent complete when patch updating
  - FOSS to docs

### Fixed

  - Client
    - Reporting of downloaded status in callbacks


## v2.1.1 - 2016/07/31

### Added

  - Docs
    - Usage docs for updating application & assets


### Fixed

  - Client
    - Restart
    - In certain cases calling download() after a failed download will not start another download
  - Parsing platform name from archive filename


## v2.1.0 - 2016/07/30

### Added

  - Retry download
  - dsdev-utils >= 0.9.0
  - Client
    - AppUpdate.extract_overwrite
    - File hash verification before extracting

### Updated

  - Client
    - Only log debug messages
    - Store update data in appdata local instead of roaming
  - archive command
  - Windows tests setup scripts
  - More concise docs

### Fixed

  - Client
    - Write file to file-system when no hash is passed
    - Close file descriptors

### Removed
  - jms-utils
  - Duplicate logging calls
  - Duplicate listing of dependencies
  - archive --target-name
  - Redundant code


###Deprecated

  - AppUpdate.win_extract_overwrite
    - Use: AppUpdate.extract_overwrite
    - Remove: v3.0
  - AppUpdate.restart
    - Use: AppUpdate.extract_restart
    - Remove: v3.0


## v2.0.5 - 2016/07/17

### Fixed

 - Creating patches


## v2.0.4 - 2016/07/17

### Added

  - Ability for windows apps to be extracted & overwritten but not restarted
  - FileDownloaderError

### Updated

  - Docs
  - Re-factored PackageHandler

### Fixed

  - Using format string while logging

## v2.0.3 - 2016/07/09

### Added

  - PyUpdater-SCP-plugin to pyupdater[all] install

### Updated

  - Install bsdiff by default
  - Lib
    - PyUpdater-SCP-plugin >= 3.0.5

### Fixed

  - User message when setting config directory


## v2.0.2 - 2016/07/09

### Updated

  - Graceful exit when attempting to import a module removed from the stdlib

### Fixed

  - Website
    - Changelog submenu


## v2.0.1 - 2016/07/09

### Fixed

  - Deploy to pypi


## v2.0 - 2016/07/09
###Backwards incompatible changes

  - Upload plugin system
    - See "Create Upload Plugins" in docs
  - Version manifest file the client downloads during update checks.
    - See "Upgrading PyUpdater" in docs

### Added

  - CLI
    - Configure where client_config.py is written
    - Plugins
      -list plugins
      - update plugin settings
      - show plugin settings
    - Verbose: Show why packages were not processed
    - Keep files after upload

### Updated

  - Plugin System
    - Simplified plugin interface
    - Enables saving of plugin configuration
    - Automatic loading of plugin configuration before use
  - Docs
    - Renamed sub menus
    - Work flow
    - Plugin Creation
    - Plugin command
    - Upgrade how to
  - License
  - File deletion on windows when uploading
  - Supports PyInstaller 3.0 - 3.2
  - Updated tests
  - Some overall clean up of the code base

### Fixed

  - Status Badges
  - Patch updates
  - Including libraries in current directory

### Removed

  - Compatibility code for older versions of PyUpdater
  - Need for specific version of PyInstaller
  - Lib
    - requests


## v1.1.15 - 2016/04/17

### Removed

  - debug code



## v1.1.14 - 2016/04/17

### Updated

  - Libs
    - PyInstaller 3.1.1
    - requests 2.9.1
    - stevedore 1.12.0
    - urllib3 1.15.1

### Fixed

  - Finding directory of executable

### Removed

  - Unused import


## v1.1.13 - 2015/12/13

### Fixed

  - Missing import


## v1.1.12 - 2015/12/13

### Removed

  - Unused dependency
    - cryptography


## v1.1.11 - 2015/12/13

### Fixed

  - Processing packages on windows


## v1.1.10 - 2015/12/13

### Fixed

  - Error when archive is in the manifest but missing from files folder
  - Error when attempting to remove executable left in new folder


## v1.1.9 - 2015/12/11

### Updated

  - Read & write files in utf-8
  - Libs
    - cryptography 1.1.2
    - stevedore 1.10.0


### Removed

  - Unused test init code


## v1.1.8 - 2015/11/23

### Updated

  - Libs
    - cryptography 1.1.1
    - certifi no longer pinned to specific version


## v1.1.7 - 2015/11/14

### Fixed

  - Parsing name of archive with spaces


## v1.1.6 - 2015/11/12

### Fixed

  - Creating second keypack for specific app


## v1.1.5 - 2015/11/08

### Updated

  - Upload Plugins
    - S3 2.5
    - SCP 2.3


## v1.1.4 - 2015/11/05

### Fixed

  - Issue restarting application when located in directories beginning with a period.


## v1.1.3 - 2015/11/04

### Fixed

  - Download progress callbacks
  - Potential issue restarting application when located in certain directories.

### Removed

  - Initializing client with list of callbacks


## v1.1.2 - 2015/10/30

### Updated

  - Cleanup of archives on dev machine
  - Centralized cleanup function to be used by client & package handler

### Fixed

  - Creating patches for updates
  - Erroneous warning when paring version info


## v1.1.1.1 - 2015/10/28

### Updated

  - Libs
    - cryptography 1.1
    - requests 2.8.1
    - stevedore 1.9.0

### Fixed

  - xrange on py3


## v1.1 - 2015/10/28

### Added

  - Make file for windows
  - Patch size in manifest
  - Release Channels
    - Alpha, Beta & Stable. Channels can be changed at anytime! Just pass the desired channel to update_check
  - Auto Upgrade external files
    - Update your external files, binaries or whatever you want to auto upgrade. Patch support included :). The absolute path to the update archive is available .abspath

### Updated

  - Pass all arguments except ones we care about directly to pyinstaller
  - CLI help messages
  - Debugging messages
  - Pre-Release versions can be in long or short form
    - Before: 1.0a 1.1.b 1.2.1b1
    - After: 1.0alpha 1.1.beta 1.2.1beta1
  - Client
    - Windows: Updates no longer open cmd prompt when restart app
    - Windows: restart scripts written to appdata instead of cwd
  - Utils
    - Make up to multiple attempts to remove a file/directory before giving up - Windows only
  - Patching
    - Will take combined size of patches and compare to the size of a full download in bytes to determine if patch update is suitable.
    - Will only create patches for packages on stable channel
    - Initial patch will start at 1 instead of 100
  - Docs
    - Commands explained with description and examples
    - Cosmetic updates

### Removed

  - Update command
  - Duplicate code
  - Build arg --app-name
    - PyUpdater will pull the app name provided during repo init


## v1.0.1 - 2015/10/11

### Updated

  - Universal wheel


## v1.0 - 2015/10/11

### Added

  - Python 3 support
  - Offline root keys
  - CI testing on windows
  - Tox testing
  - ETA provided to callbacks
  - Async download
    - download(async=True)

### Updated

  - Client
    - Support for offline root keys
    - Sanitizing url attributes
    - Patches clients up to 4 versions behind
  - Config is now a dict instead of class
  - Logging errors for 3rd party services
  - Info messages
  - Storage object
    - JSON backed
    - Centralized data store
  - ClI
    - help messages
    - offline keys are created and imported
    - importing keys overwrites currently imported key
  - Optimized tests
    - Centralized PyUpdater object creation
    - Test filename generators
  - Libs
    - urllib3 1.12
    - requests 2.8.0
  - Simplified signature verification

### Fixed

  - Error when not able to get cpu count on windows
  - Writing debug
  - Uploading debug logs

### Removed

  - vendored pyinstaller
  - revoking keys
  - Some unused code
    - PyUpdaterConfig

## v0.23.3 - 2015/07/21

### Fixed

  - File already exists error

## v0.23.2 - 2015/07/21

### Fixed

  - Compilation

### Updated

  - PyInstaller to 39b02fe5e7563431115f9812f757a21bbcc78837


## v0.23.1 - 2015/07/19

### Fixed

  - Missing bootloaders


## v0.23.0 - 2015/07/19

### Added

  - Vendored PyInstaller

    - f920d3eea510ed088eda5359c04990338600c2b8
    - Ability to provide fixes quicker

### Fixed

  - Error when patch info is None


## v0.22.3 - 2015/07/18

### Fixed

  - Parsing platform names


## v0.22.2 - 2015/07/18

### Fixed

  - Versioneer settings


## v0.22.1 - 2015/07/18

### Updated

  - Versioneer settings



## v0.22 - 2015/07/18

### Updated

  - Code refactoring & optimizations

  - Download url

  - Converted docs to markdown

  - Error handling for callbacks

  - Libs

    - ed15519 1.4
    - stevedore 1.6.0
    - PyUpdater-S3-Plugin 2.3

### Removed

  - Duplicate code
  - Deprecated log command

## v0.21.1 - 2015/05/25

### Added

  * More hooks from pyinstaller develop

### Updated

  * Test runs in parallel
  * Documentation
  * Libs
    - requests 2.7.0
    - urllib3 1.10.4

### Fixed

  - Parsing App Name from update archive filename when version number is in x.x format
  - Potential import error if pyinstaller version lower then 2.1

### Removed

  - Unused code


## v0.21.0 - 2015/04/30

### Updated

  - PyUpdater

    - Debug logs are uploaded to a gist on github
    - requests lib 2.6.2
    - urllib3 lib 1.10.3
    - stevedore lib 1.4.0
    - S3 plugin 2.2
    - SCP plugin 2.2
    - Code refactoring

### Fixed

  - PyUpdater

    - Potential leak of sensitive information to log files


## v0.20.0 - 2015/03/08
#### Renamed to PyUpdater

### Updated

  - Client

    - Better error handling

  - PyUpdater

    - Using json to store config data
    - Less IO during execution
    - Header performance improvements - upstream
    - Central db object

### Fixed

  - Client

    - Handling of download with corresponding hash

  - PyUpdater

    - session fixation attacks and potentially cookie stealing - upstream
    - Not writing config file when cleaning repo

### Removed

  - PyUpdater

    - RC4 from default cipher list - upstream
    - Old migration code
    - Removed old json version file
    - Download progress to stdout
    - Unused imports


## v0.19.3 - 2015/02/22

### Fixed

  - Client

    - Removing old updates. Really fixed it this time :)


## v0.19.2 - 2015/02/22

### Fixed

  - Client

    - Removing old updates


## v0.19.1 - 2015/02/22

### Fixed

  - PyUpdater

    - Creating new config db when running any command


## v0.19 - 2015/02/22

### Added

  - CLI

    - Update command. Used after updating PyUpdater to update repository

  - Logging

    - Now logs framework version

### Updated

  - CLI

    - Clearer output messages
    - Correct some spelling

  - Client

    - Exception handling
    - Moved patcher and downloader to client package
    - Using requests instead of urllib3.
    - More reliable https verification

  - PyUpdater

    - Potential incorrect comparison of pyinstaller versions
    - Archive version parsing
    - Crashing if directory does not exists
    - Pinning version of plugins
    - Initial support for pre release versions
    - Moved some uploader config to plugins. Check plugin docs for more info.
    - Updated config attributes. * Make sure to run pyupdater update
    - Install commands

      $ pip install[patch] # To enable patch support
      $ pip install[all] # To add patch support, aws s3 & scp upload plugins

  - Plugins

    - from pyi_updater.uploader import BaseUploader
    - from pyi_updater.uploader.common import BaseUploader will
      be remove in v0.22+

### Fixed

  - Key Handler

    - Writing of deprecated version meta after migration
    - Not loading keys from db

  - Package Handler

    - Migration of repo meta config

  - PyUpdater

    - Potential error when adding key add key.db isn't loaded

### Removed

  - PyUpdater

    - Some unused attributes on config object
    - Unused functions
