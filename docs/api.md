# API documentation



## Table of contents

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

Used to check for updates & returns an updateobject if there is an update.

Kwargs:

    obj (instance): config object

    refresh (bool) Meaning:

        True: Refresh update manifest on object initialization

        False: Don't refresh update manifest on object initialization

    progress_hooks (list) List of callbacks

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

Checks for available updates

Args:

    name (str): Name of file to update

    version (str): Current version number of file to update

    channel (str): Release channel

Returns:

    (updateobject) Meanings:

        AppUpdate - Used to update current binary

        LibUpdate - Used to update external assets

        None - No Updates available

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

