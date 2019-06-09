# Upgrading PyUpdater
Note: Major version will maintain API compatibility.

## To PyUpdater >= 3.0

You need to change the download signature
```
AppUpdate.download(async=True) 
# To
AppUpdate.download(background=True)

LibUpdate.download(async=True)
# To
LibUpdate.download(background=True)
```


## To PyUpdater >= 2.0.3
Deprecated since bsdiff4 is installed by default.

```
$ pip install pyupdater[patch]
```

## To PyUpdater >= 2.0
Coming from PyUpdater >= 1.1
1. Run the command below
2. Press enter to use the default value.

```
$ pyupdater settings --config-path
```
Coming from PyUpdater < 1.1
1. You'll need to update to PyUpdater 1.1.15
2. If using progress hooks note that progress_hook changed to progress_hooks and only accepts lists
3. Release a new version of your application that uses PyUpdater 1.1.15
4. Ensure all end users are using the latest version of your application.
5. Once all of your end users have the latest version or your application, you can upgrade to PyUpdater 2.0

This extra step is required because the schema of the version manifest file changed to support release channels. Version 1.1 was released about 7+ months ago. Future releases will document, in the changelog, when backwards compatibility code is marked for deprecation.