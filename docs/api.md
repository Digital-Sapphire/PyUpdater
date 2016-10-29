# API documentation of pyupdater



## Table of contents

### [pyupdater.cli](#pyupdatercli)

* [pyupdater.cli.archive](#pyupdatercliarchiveargs)
* [pyupdater.cli.ask_yes_no](#pyupdatercliask_yes_noquestion-defaultno-answernone)
* [pyupdater.cli.build](#pyupdaterclibuildargs-pyi_args)
* [pyupdater.cli.check_repo](#pyupdaterclicheck_repo)
* [pyupdater.cli.clean](#pyupdaterclicleanargs)
* [pyupdater.cli.get_correct_answer](#pyupdatercliget_correct_answerquestion-defaultnone-requiredfalse-answernone-is_answer_correctnone)
* [pyupdater.cli.get_http_pool](#pyupdatercliget_http_poolsecuretrue)
* [pyupdater.cli.get_parser](#pyupdatercliget_parser)
* [pyupdater.cli.init](#pyupdatercliinit)
* [pyupdater.cli.initial_setup](#pyupdatercliinitial_setupconfig)
* [pyupdater.cli.keys](#pyupdaterclikeysargs)
* [pyupdater.cli.main](#pyupdaterclimainargsnone)
* [pyupdater.cli.make_spec](#pyupdaterclimake_specargs-pyi_args)
* [pyupdater.cli.pkg](#pyupdaterclipkgargs)
* [pyupdater.cli.plugins](#pyupdatercliplugins)
* [pyupdater.cli.print_plugin_settings](#pyupdatercliprint_plugin_settingsplugin_name-config)
* [pyupdater.cli.remove_any](#pyupdatercliremove_anypath)
* [pyupdater.cli.setting](#pyupdaterclisettingargs)
* [pyupdater.cli.setup_client_config_path](#pyupdaterclisetup_client_config_pathconfig)
* [pyupdater.cli.setup_company](#pyupdaterclisetup_companyconfig)
* [pyupdater.cli.setup_max_download_retries](#pyupdaterclisetup_max_download_retriesconfig)
* [pyupdater.cli.setup_patches](#pyupdaterclisetup_patchesconfig)
* [pyupdater.cli.setup_plugin](#pyupdaterclisetup_pluginname-config)
* [pyupdater.cli.setup_urls](#pyupdaterclisetup_urlsconfig)
* [pyupdater.cli.upload](#pyupdatercliuploadargs)
* [pyupdater.cli.upload_debug_info](#pyupdatercliupload_debug_info)
* [pyupdater.cli.user_log_dir](#pyupdatercliuser_log_dirappnamenone-appauthornone-versionnone-opiniontrue)
* [pyupdater.cli.Builder](#pyupdaterclibuilder)
* [pyupdater.cli.ChDir](#pyupdaterclichdir)
* [pyupdater.cli.Config](#pyupdatercliconfig)
* [pyupdater.cli.ExternalLib](#pyupdatercliexternallib)
* [pyupdater.cli.KeyImporter](#pyupdaterclikeyimporter)
* [pyupdater.cli.Keys](#pyupdaterclikeys)
* [pyupdater.cli.Loader](#pyupdatercliloader)
* [pyupdater.cli.PluginManager](#pyupdaterclipluginmanager)
* [pyupdater.cli.PyUpdater](#pyupdaterclipyupdater)
* [pyupdater.cli.UploaderError](#pyupdatercliuploadererror)
* [pyupdater.cli.UploaderPluginError](#pyupdatercliuploaderpluginerror)


### [pyupdater.client](#pyupdaterclient)

* [pyupdater.client.get_highest_version](#pyupdaterclientget_highest_versionname-plat-channel-easy_data)
* [pyupdater.client.get_system](#pyupdaterclientget_system)
* [pyupdater.client.gzip_decompress](#pyupdaterclientgzip_decompressdata)
* [pyupdater.client.AppUpdate](#pyupdaterclientappupdate)
* [pyupdater.client.ChDir](#pyupdaterclientchdir)
* [pyupdater.client.Client](#pyupdaterclientclient)
* [pyupdater.client.Config](#pyupdaterclientconfig)
* [pyupdater.client.EasyAccessDict](#pyupdaterclienteasyaccessdict)
* [pyupdater.client.FileDownloader](#pyupdaterclientfiledownloader)
* [pyupdater.client.LibUpdate](#pyupdaterclientlibupdate)
* [pyupdater.client.Version](#pyupdaterclientversion)


### [pyupdater.hooks](#pyupdaterhooks)

* [pyupdater.hooks.get_hook_dir](#pyupdaterhooksget_hook_dir)


### [pyupdater.key_handler](#pyupdaterkey_handler)

* [pyupdater.key_handler.lazy_import](#pyupdaterkey_handlerlazy_importfunc)
* [pyupdater.key_handler.KeyHandler](#pyupdaterkey_handlerkeyhandler)
* [pyupdater.key_handler.Storage](#pyupdaterkey_handlerstorage)


### [pyupdater.package_handler](#pyupdaterpackage_handler)

* [pyupdater.package_handler.get_package_hashes](#pyupdaterpackage_handlerget_package_hashesfilename)
* [pyupdater.package_handler.get_size_in_bytes](#pyupdaterpackage_handlerget_size_in_bytesfilename)
* [pyupdater.package_handler.lazy_import](#pyupdaterpackage_handlerlazy_importfunc)
* [pyupdater.package_handler.remove_dot_files](#pyupdaterpackage_handlerremove_dot_filesfiles)
* [pyupdater.package_handler.remove_previous_versions](#pyupdaterpackage_handlerremove_previous_versionsdirectory-filename)
* [pyupdater.package_handler.EasyAccessDict](#pyupdaterpackage_handlereasyaccessdict)
* [pyupdater.package_handler.Package](#pyupdaterpackage_handlerpackage)
* [pyupdater.package_handler.PackageHandler](#pyupdaterpackage_handlerpackagehandler)
* [pyupdater.package_handler.PackageHandlerError](#pyupdaterpackage_handlerpackagehandlererror)
* [pyupdater.package_handler.Patch](#pyupdaterpackage_handlerpatch)
* [pyupdater.package_handler.Storage](#pyupdaterpackage_handlerstorage)


### [pyupdater.utils](#pyupdaterutils)

* [pyupdater.utils.check_repo](#pyupdaterutilscheck_repo)
* [pyupdater.utils.create_asset_archive](#pyupdaterutilscreate_asset_archivename-version)
* [pyupdater.utils.dict_to_str_sanatize](#pyupdaterutilsdict_to_str_sanatizedata)
* [pyupdater.utils.get_size_in_bytes](#pyupdaterutilsget_size_in_bytesfilename)
* [pyupdater.utils.initial_setup](#pyupdaterutilsinitial_setupconfig)
* [pyupdater.utils.lazy_import](#pyupdaterutilslazy_importfunc)
* [pyupdater.utils.make_archive](#pyupdaterutilsmake_archivename-target-version)
* [pyupdater.utils.pretty_time](#pyupdaterutilspretty_timesec)
* [pyupdater.utils.print_plugin_settings](#pyupdaterutilsprint_plugin_settingsplugin_name-config)
* [pyupdater.utils.remove_any](#pyupdaterutilsremove_anypath)
* [pyupdater.utils.remove_dot_files](#pyupdaterutilsremove_dot_filesfiles)
* [pyupdater.utils.run](#pyupdaterutilsruncmd)
* [pyupdater.utils.setup_appname](#pyupdaterutilssetup_appnameconfig)
* [pyupdater.utils.setup_client_config_path](#pyupdaterutilssetup_client_config_pathconfig)
* [pyupdater.utils.setup_company](#pyupdaterutilssetup_companyconfig)
* [pyupdater.utils.setup_max_download_retries](#pyupdaterutilssetup_max_download_retriesconfig)
* [pyupdater.utils.setup_patches](#pyupdaterutilssetup_patchesconfig)
* [pyupdater.utils.setup_plugin](#pyupdaterutilssetup_pluginname-config)
* [pyupdater.utils.setup_urls](#pyupdaterutilssetup_urlsconfig)
* [pyupdater.utils.ChDir](#pyupdaterutilschdir)
* [pyupdater.utils.ExtensionManager](#pyupdaterutilsextensionmanager)
* [pyupdater.utils.JSONStore](#pyupdaterutilsjsonstore)
* [pyupdater.utils.PluginManager](#pyupdaterutilspluginmanager)
* [pyupdater.utils.DictMixin](#pyupdaterutilsdictmixin)




## pyupdater.cli



##### pyupdater.cli.archive(args)



##### pyupdater.cli.ask_yes_no(question, default='no', answer=None)

Will ask a question and keeps prompting until
answered.

Args:

    question (str): Question to ask end user

    default (str): Default answer if user just press enter at prompt

    answer (str): Used for testing

Returns:

    (bool) Meaning:

        True - Answer is  yes

        False - Answer is no

##### pyupdater.cli.build(args, pyi_args)



##### pyupdater.cli.check_repo()

Checks if current directory is a pyupdater repository

##### pyupdater.cli.clean(args)



##### pyupdater.cli.get_correct_answer(question, default=None, required=False, answer=None, is_answer_correct=None)

Ask user a question and confirm answer

Args:

    question (str): Question to ask user

    default (str): Default answer if no input from user

    required (str): Require user to input answer

    answer (str): Used for testing

    is_answer_correct (str): Used for testing

##### pyupdater.cli.get_http_pool(secure=True)



##### pyupdater.cli.get_parser()



##### pyupdater.cli.init()



##### pyupdater.cli.initial_setup(config)



##### pyupdater.cli.keys(args)



##### pyupdater.cli.main(args=None)



##### pyupdater.cli.make_spec(args, pyi_args)



##### pyupdater.cli.pkg(args)



##### pyupdater.cli.plugins()



##### pyupdater.cli.print_plugin_settings(plugin_name, config)



##### pyupdater.cli.remove_any(path)



##### pyupdater.cli.setting(args)



##### pyupdater.cli.setup_client_config_path(config)



##### pyupdater.cli.setup_company(config)



##### pyupdater.cli.setup_max_download_retries(config)



##### pyupdater.cli.setup_patches(config)



##### pyupdater.cli.setup_plugin(name, config)



##### pyupdater.cli.setup_urls(config)



##### pyupdater.cli.upload(args)



##### pyupdater.cli.upload_debug_info()



##### pyupdater.cli.user_log_dir(appname=None, appauthor=None, version=None, opinion=True)

Return full path to the user-specific log dir for this application.

    "appname" is the name of application.
        If None, just the system directory is returned.
    "appauthor" (only used on Windows) is the name of the
        appauthor or distributing body for this application. Typically
        it is the owning company name. This falls back to appname. You may
        pass False to disable it.
    "version" is an optional version path element to append to the
        path. You might want to use this if you want multiple versions
        of your app to be able to run independently. If used, this
        would typically be "<major>.<minor>".
        Only applied when appname is present.
    "opinion" (boolean) can be False to disable the appending of
        "Logs" to the base app data dir for Windows, and "log" to the
        base cache dir for Unix. See discussion below.

Typical user cache directories are:
    Mac OS X:   ~/Library/Logs/<AppName>
    Unix:       ~/.cache/<AppName>/log  # or under $XDG_CACHE_HOME if defined
    Win XP:     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>\Logs
    Vista:      C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>\Logs

On Windows the only suggestion in the MSDN docs is that local settings
go in the `CSIDL_LOCAL_APPDATA` directory. (Note: I'm interested in
examples of what some windows apps use for a logs dir.)

OPINION: This function appends "Logs" to the `CSIDL_LOCAL_APPDATA`
value for Windows and appends "log" to the user cache dir for Unix.
This can be disabled with the `opinion=False` option.

### pyupdater.cli.Builder

Wrapper for Pyinstaller with some extras. After building
executable with pyinstaller, Builder will create an archive
of the executable.

Args:

    args (list): Args specific to PyUpdater

    pyi_args (list): Args specific to Pyinstaller

#### Methods

##### Builder.build()



##### Builder.make_spec()



#### Properties

### pyupdater.cli.ChDir

Used as a context manager to step into a directory
do some work then return to the original directory.

Args:

    path (str): Absolute path to directory you want to change to

#### Methods

#### Properties

### pyupdater.cli.Config



#### Methods

##### Config.from_object(obj)

Updates the values from the given object

Args:

    obj (instance): Object with config attributes

Objects are classes.

Just the uppercase variables in that object are stored in the config.
Example usage::

    from yourapplication import default_config
    app.config.from_object(default_config())

#### Properties

### pyupdater.cli.ExternalLib



#### Methods

##### ExternalLib.archive()



#### Properties

### pyupdater.cli.KeyImporter



#### Methods

##### KeyImporter.start()



#### Properties

### pyupdater.cli.Keys



#### Methods

##### Keys.make_keypack(name)



#### Properties

### pyupdater.cli.Loader

Loads &  saves config file

#### Methods

##### Loader.get_app_name()



##### Loader.load_config()

Loads config from database (json file)

Returns (obj): Config object

##### Loader.save_config(obj)

Saves config file to pyupdater database

Args:

    obj (obj): config object

#### Properties

### pyupdater.cli.PluginManager



#### Methods

##### PluginManager.config_plugin(name, config)



##### PluginManager.get_plugin(name, init=False)

Returns the named plugin

##### PluginManager.get_plugin_names()

Returns the name & author of all installed
plugins

##### PluginManager.get_plugin_settings(name)



#### Properties

### pyupdater.cli.PyUpdater

Processes, signs & uploads updates

Kwargs:

    config (obj): config object

#### Methods

##### PyUpdater.get_plugin_names()



##### PyUpdater.import_keypack()

Creates signing keys

##### PyUpdater.process_packages(report_errors=False)

Creates hash for updates & adds information about update to
version file

##### PyUpdater.set_uploader(requested_uploader, keep=False)

Sets upload destination

Args:

    requested_uploader (str): upload service. i.e. s3, scp

##### PyUpdater.setup()

Sets up root dir with required PyUpdater folders

##### PyUpdater.sign_update()

Signs version file with signing key

##### PyUpdater.update_config(config)

Updates internal config

Args:

    config (obj): config object

##### PyUpdater.upload()

Uploads files in deploy folder

#### Properties

### pyupdater.cli.UploaderError

Raised for Uploader exceptions

#### Methods

##### UploaderError.format_traceback()



#### Properties

### pyupdater.cli.UploaderPluginError

Raised for Uploader exceptions

#### Methods

##### UploaderPluginError.format_traceback()



#### Properties

## pyupdater.client



##### pyupdater.client.get_highest_version(name, plat, channel, easy_data)

Parses version file and returns the highest version number.

Args:

   name (str): name of file to search for updates

   plat (str): the platform we are requesting for

   channel (str): the release channel

   easy_data (dict): data file to search

Returns:

   (str) Highest version number

##### pyupdater.client.get_system()



##### pyupdater.client.gzip_decompress(data)

Decompress gzip data

Args:

    data (str): Gzip data


Returns:

    (data): Decompressed data

### pyupdater.client.AppUpdate

Used to update library files used by an application

Args:

    data (dict): Info dict

#### Methods

##### AppUpdate.cleanup()



##### AppUpdate.download(async=False)



##### AppUpdate.extract()

Will extract archived update and leave in update folder.
If updating a lib you can take over from there. If updating
an app this call should be followed by :meth:`restart` to
complete update.

Returns:

    (bool) Meanings:

        True - Extract successful

        False - Extract failed

##### AppUpdate.extract_overwrite()

Will extract the update then overwrite the current app

##### AppUpdate.extract_restart()

Will extract the update, overwrite the current app,
then restart the app using the updated binary.

##### AppUpdate.is_downloaded()

Returns (bool):

True: File is already downloaded.

False: File hasn't been downloaded.

##### AppUpdate.restart()

Will overwrite old binary with updated binary and
restart using the updated binary. Not supported on windows.

##### AppUpdate.win_extract_overwrite()



#### Properties

### pyupdater.client.ChDir

Used as a context manager to step into a directory
do some work then return to the original directory.

Args:

    path (str): Absolute path to directory you want to change to

#### Methods

#### Properties

### pyupdater.client.Client

Used on client side to update files

Kwargs:

    obj (instance): config object

    refresh (bool) Meaning:

        True: Refresh update manifest on object initialization

        False: Don't refresh update manifest on object initialization

    call_back (func): Used for download progress

#### Methods

##### Client.add_progress_hook(cb)



##### Client.init_app(obj, refresh=False, test=False)

Sets up client with config values from obj

Args:

    obj (instance): config object

Kwargs:

    refresh (bool) Meaning:

    True: Refresh update manifest on object initialization

    False: Don't refresh update manifest on object initialization

##### Client.refresh()

Will download and verify your version file.

##### Client.update_check(name, version, channel=u'stable')

Will try to patch binary if all check pass.  IE hash verified
signature verified.  If any check doesn't pass then falls back to
full update

Args:

    name (str): Name of file to update

    version (str): Current version number of file to update

    channel (str): Release channel

Returns:

    (bool) Meanings:

        True - Update Successful

        False - Update Failed

#### Properties

### pyupdater.client.Config



#### Methods

##### Config.from_object(obj)

Updates the values from the given object

Args:

    obj (instance): Object with config attributes

Objects are classes.

Just the uppercase variables in that object are stored in the config.
Example usage::

    from yourapplication import default_config
    app.config.from_object(default_config())

#### Properties

### pyupdater.client.EasyAccessDict

Provides access to dict by pass a specially made key to
the get method. Default key sep is "*". Example key would be
updates*mac*1.7.0 would access {"updates":{"mac":{"1.7.0": "hi there"}}}
and return "hi there"

Kwargs:

    dict_ (dict): Dict you would like easy asses to.

    sep (str): Used as a delimiter between keys

#### Methods

#### Properties

### pyupdater.client.FileDownloader

The FileDownloader object downloads files to memory and
verifies their hash.  If hash is verified data is either
written to disk to returned to calling object

Args:

    filename (str): The name of file to download

    urls (list): List of urls to use for file download

Kwargs:

    hexdigest (str): The hash of the file to download

    verify (bool) Meaning:

        True: Verify https connection

        False: Don't verify https connection

#### Methods

##### FileDownloader.download_verify_return()

Downloads file to memory, checks against provided hash
If matched returns binary data

Returns:

    (data) Meanings:

        Binary data - If hashes match or no hash was given during
        initialization.

        None - If any verification didn't pass

##### FileDownloader.download_verify_write()

Downloads file then verifies against provided hash
If hash verfies then writes data to disk

Returns:

    (bool) Meanings:

        True - Hashes match or no hash was given during initialization.

        False - Hashes don't match

#### Properties

### pyupdater.client.LibUpdate

Used to update library files used by an application

Args:

    data (dict): Info dict

#### Methods

##### LibUpdate.cleanup()



##### LibUpdate.download(async=False)



##### LibUpdate.extract()

Will extract archived update and leave in update folder.
If updating a lib you can take over from there. If updating
an app this call should be followed by :meth:`restart` to
complete update.

Returns:

    (bool) Meanings:

        True - Extract successful

        False - Extract failed

##### LibUpdate.is_downloaded()

Returns (bool):

True: File is already downloaded.

False: File hasn't been downloaded.

#### Properties

### pyupdater.client.Version

Normalizes version strings of different types. Examples
include 1.2, 1.2.1, 1.2b and 1.1.1b

Args:

    version (str): Version number to normalizes

#### Methods

#### Properties

## pyupdater.hooks



##### pyupdater.hooks.get_hook_dir()



## pyupdater.key_handler



##### pyupdater.key_handler.lazy_import(func)

Decorator for declaring a lazy import.

This decorator turns a function into an object that will act as a lazy
importer.  Whenever the object's attributes are accessed, the function
is called and its return value used in place of the object.  So you
can declare lazy imports like this:

    @lazy_import
    def socket():
        import socket
        return socket

The name "socket" will then be bound to a transparent object proxy which
will import the socket module upon first use.

The syntax here is slightly more verbose than other lazy import recipes,
but it's designed not to hide the actual "import" statements from tools
like pyinstaller or grep.

### pyupdater.key_handler.KeyHandler

KeyHanlder object is used to manage keys used for signing updates

Kwargs:

    app (obj): Config object to get config values from

#### Methods

##### KeyHandler.sign_update()

Signs version file with private key

Proxy method for :meth:`_add_sig`

#### Properties

### pyupdater.key_handler.Storage



#### Methods

##### Storage.load(key)

Loads value for given key

Args:

    key (str): The key associated with the value you want
    form the database.

Returns:

    Object if exists or else None

##### Storage.save(key, value)

Saves key & value to database

Args:

    key (str): used to retrieve value from database

    value (obj): python object to store in database

#### Properties

## pyupdater.package_handler



##### pyupdater.package_handler.get_package_hashes(filename)

Provides hash of given filename.

Args:

    filename (str): Name of file to hash

Returns:

    (str): sha256 hash

##### pyupdater.package_handler.get_size_in_bytes(filename)



##### pyupdater.package_handler.lazy_import(func)

Decorator for declaring a lazy import.

This decorator turns a function into an object that will act as a lazy
importer.  Whenever the object's attributes are accessed, the function
is called and its return value used in place of the object.  So you
can declare lazy imports like this:

    @lazy_import
    def socket():
        import socket
        return socket

The name "socket" will then be bound to a transparent object proxy which
will import the socket module upon first use.

The syntax here is slightly more verbose than other lazy import recipes,
but it's designed not to hide the actual "import" statements from tools
like pyinstaller or grep.

##### pyupdater.package_handler.remove_dot_files(files)

Removes hidden dot files from file list

Args:

    files (list): List of file names

Returns:

    (list): List of filenames with ".example" files removed.

##### pyupdater.package_handler.remove_previous_versions(directory, filename)

Removes previous version of named file

### pyupdater.package_handler.EasyAccessDict

Provides access to dict by pass a specially made key to
the get method. Default key sep is "*". Example key would be
updates*mac*1.7.0 would access {"updates":{"mac":{"1.7.0": "hi there"}}}
and return "hi there"

Kwargs:

    dict_ (dict): Dict you would like easy asses to.

    sep (str): Used as a delimiter between keys

#### Methods

#### Properties

### pyupdater.package_handler.Package

Holds information of update file.

Args:

    filename (str): name of update file

#### Methods

##### Package.extract_info(package)

Gets version number, platform & hash for package.

Args:

    package (str): filename

#### Properties

### pyupdater.package_handler.PackageHandler

Handles finding, sorting, getting meta-data, moving packages.

Kwargs:

    app (instance): Config object

#### Methods

##### PackageHandler.init_app(obj)

Sets up client with config values from obj

Args:

    obj (instance): config object

##### PackageHandler.process_packages(report_errors=False)

Gets a list of updates to process.  Adds the name of an
update to the version file if not already present.  Processes
all packages.  Updates the version file meta-data. Then writes
version file back to disk.

##### PackageHandler.setup()

Creates working directories & loads json files.

#### Properties

### pyupdater.package_handler.PackageHandlerError

Raised for PackageHandler exceptions

#### Methods

##### PackageHandlerError.format_traceback()



#### Properties

### pyupdater.package_handler.Patch

Holds information for patch file.

Args:

    patch_info (dict): patch information

#### Methods

#### Properties

### pyupdater.package_handler.Storage



#### Methods

##### Storage.load(key)

Loads value for given key

Args:

    key (str): The key associated with the value you want
    form the database.

Returns:

    Object if exists or else None

##### Storage.save(key, value)

Saves key & value to database

Args:

    key (str): used to retrieve value from database

    value (obj): python object to store in database

#### Properties

## pyupdater.utils



##### pyupdater.utils.check_repo()

Checks if current directory is a pyupdater repository

##### pyupdater.utils.create_asset_archive(name, version)

Used to make archives of file or dir. Zip on windows and tar.gz
on all other platforms

Args:
    name - Name to rename binary.

    version - Version of app. Used to create archive filename

Returns:
     (str) - name of archive

##### pyupdater.utils.dict_to_str_sanatize(data)



##### pyupdater.utils.get_size_in_bytes(filename)



##### pyupdater.utils.initial_setup(config)



##### pyupdater.utils.lazy_import(func)

Decorator for declaring a lazy import.

This decorator turns a function into an object that will act as a lazy
importer.  Whenever the object's attributes are accessed, the function
is called and its return value used in place of the object.  So you
can declare lazy imports like this:

    @lazy_import
    def socket():
        import socket
        return socket

The name "socket" will then be bound to a transparent object proxy which
will import the socket module upon first use.

The syntax here is slightly more verbose than other lazy import recipes,
but it's designed not to hide the actual "import" statements from tools
like pyinstaller or grep.

##### pyupdater.utils.make_archive(name, target, version)

Used to make archives of file or dir. Zip on windows and tar.gz
on all other platforms

Args:
    name - Name to rename binary.

    version - Version of app. Used to create archive filename

    target - Name of file to archive.

Returns:
     (str) - name of archive

##### pyupdater.utils.pretty_time(sec)

Turns seconds into a human readable format. Example: 2020/07/31 12:22:83

Args:

    sec (int): seconds since unix epoch

Returns:

    (str): Human readable time

##### pyupdater.utils.print_plugin_settings(plugin_name, config)



##### pyupdater.utils.remove_any(path)



##### pyupdater.utils.remove_dot_files(files)

Removes hidden dot files from file list

Args:

    files (list): List of file names

Returns:

    (list): List of filenames with ".example" files removed.

##### pyupdater.utils.run(cmd)

Logs a command before running it in subprocess.

Args:

    cmd (str): command to be ran in subprocess

Returns:

    (int): Exit code

##### pyupdater.utils.setup_appname(config)



##### pyupdater.utils.setup_client_config_path(config)



##### pyupdater.utils.setup_company(config)



##### pyupdater.utils.setup_max_download_retries(config)



##### pyupdater.utils.setup_patches(config)



##### pyupdater.utils.setup_plugin(name, config)



##### pyupdater.utils.setup_urls(config)



### pyupdater.utils.ChDir

Used as a context manager to step into a directory
do some work then return to the original directory.

Args:

    path (str): Absolute path to directory you want to change to

#### Methods

#### Properties

### pyupdater.utils.ExtensionManager

Base class for all of the other managers.

:param namespace: The namespace for the entry points.
:type namespace: str
:param invoke_on_load: Boolean controlling whether to invoke the
    object returned by the entry point after the driver is loaded.
:type invoke_on_load: bool
:param invoke_args: Positional arguments to pass when invoking
    the object returned by the entry point. Only used if invoke_on_load
    is True.
:type invoke_args: tuple
:param invoke_kwds: Named arguments to pass when invoking
    the object returned by the entry point. Only used if invoke_on_load
    is True.
:type invoke_kwds: dict
:param propagate_map_exceptions: Boolean controlling whether exceptions
    are propagated up through the map call or whether they are logged and
    then ignored
:type propagate_map_exceptions: bool
:param on_load_failure_callback: Callback function that will be called when
    a entrypoint can not be loaded. The arguments that will be provided
    when this is called (when an entrypoint fails to load) are
    (manager, entrypoint, exception)
:type on_load_failure_callback: function
:param verify_requirements: Use setuptools to enforce the
    dependencies of the plugin(s) being loaded. Defaults to False.
:type verify_requirements: bool

#### Methods

#### Properties

### pyupdater.utils.JSONStore



#### Methods

##### JSONStore.copy()



##### JSONStore.keys()



##### JSONStore.sync(json_kw=None, force=False)

Atomically write the entire store to disk if it's changed.
If a dict is passed in as `json_kw`, it will be used as keyword
arguments to the json module.
If force is set True, a new file will be written even if the store
hasn't changed since last sync.

#### Properties

### pyupdater.utils.PluginManager



#### Methods

##### PluginManager.config_plugin(name, config)



##### PluginManager.get_plugin(name, init=False)

Returns the named plugin

##### PluginManager.get_plugin_names()

Returns the name & author of all installed
plugins

##### PluginManager.get_plugin_settings(name)



#### Properties

### pyupdater.utils.DictMixin



#### Methods

#### Properties

