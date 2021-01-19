# API



## Table of contents

### [pyupdater.client](#pyupdaterclient)

* [pyupdater.client.get_highest_version](#pyupdaterclientget_highest_versionname-plat-channel-easy_data-strict)
* [pyupdater.client.AppUpdate](#pyupdaterclientappupdate)
* [pyupdater.client.Client](#pyupdaterclientclient)
* [pyupdater.client.ClientError](#pyupdaterclientclienterror)
* [pyupdater.client.DefaultClientConfig](#pyupdaterclientdefaultclientconfig)
* [pyupdater.client.LibUpdate](#pyupdaterclientlibupdate)




## pyupdater.client



##### pyupdater.client.get_highest_version(name, plat, channel, easy_data, strict)



### pyupdater.client.AppUpdate

Used to update an application. This object is returned by
pyupdater.client.Client.update_check

Args:

    data (dict): Info dict

#### Methods

##### AppUpdate.cleanup()

Cleans up old update archives for this app or asset

##### AppUpdate.download(background=False)

Downloads update

######Args:

    background (bool): Perform download in background thread

##### AppUpdate.extract()

Will extract the update from its archive to the update folder.
If updating a lib you can take over from there. If updating
an app this call should be followed by method "restart" to
complete update.

######Returns:

    (bool) True - Extract successful. False - Extract failed.

##### AppUpdate.extract_overwrite()

Will extract the update then overwrite the current binary

##### AppUpdate.extract_restart()

Will extract the update, overwrite the current binary,
then restart the application using the updated binary.

##### AppUpdate.is_downloaded()

Used to check if update has been downloaded.

######Returns (bool):

    True - File is already downloaded.

    False - File has not been downloaded.

### pyupdater.client.Client

Used to check for updates & returns an updateobject if there
is an update.

######Args:

obj (instance): config object

######Kwargs:

refresh (bool): True - Refresh update manifest on init
                False - Don't refresh update manifest on init

progress_hooks (list): List of callbacks

data_dir (str): Path to custom update folder

headers (dict): A dictionary of generic and/or urllib3.utils.make_headers compatible headers

strategy (str): The update strategy to use.  By default, the overwrite
strategy is used.  Accepts any of `UpdateStrategy.DEFAULT`,
`UpdateStrategy.OVERWRITE`, and `UpdateStrategy.RENAME`.  The rename strategy
is only available on Windows for single file bundles. Instead of overwriting the binary
in place, it renames and hides the currently executing app to make place for the
new executable.  This is useful if you encounter antivirus warnings using the overwrite strategy
on Windows, which relies .vbs and .bat files.

test (bool): Used to initialize a test client

#### Methods

##### Client.add_progress_hook(cb)

Add a download progress callback function to the list of progress
hooks.

total:  Total size of the file to download

downloaded: The amount of bytes that have been downloaded so far.

percent_complete: The percentage downloaded so far

status: Status of download

Args:

cb (function): Function which takes a dict as its first argument

##### Client.refresh()

Will download and verify the version manifest.

##### Client.update_check(name, version, channel='stable', strict=True)

Checks for available updates

######Args:

name (str): Name of file to update

version (str): Current version number of file to update

channel (str): Release channel

strict (bool):
    True - Only look for updates on specified channel.
    False - Look for updates on all channels

######Returns:

(updateobject):

    AppUpdate - Used to update current binary

    LibUpdate - Used to update external assets

    None - No Updates available

### pyupdater.client.ClientError

Raised for Client exceptions

#### Methods

##### ClientError.format_traceback()



### pyupdater.client.DefaultClientConfig



#### Methods

### pyupdater.client.LibUpdate

Used to update library files used by an application. This object is
returned by pyupdater.client.Client.update_check

######Args:

data (dict): Info dict

#### Methods

##### LibUpdate.cleanup()

Cleans up old update archives for this app or asset

##### LibUpdate.download(background=False)

Downloads update

######Args:

    background (bool): Perform download in background thread

##### LibUpdate.extract()

Will extract the update from its archive to the update folder.
If updating a lib you can take over from there. If updating
an app this call should be followed by method "restart" to
complete update.

######Returns:

    (bool) True - Extract successful. False - Extract failed.

##### LibUpdate.is_downloaded()

Used to check if update has been downloaded.

######Returns (bool):

    True - File is already downloaded.

    False - File has not been downloaded.

