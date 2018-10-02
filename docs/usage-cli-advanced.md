#Usage | CLI | Advanced
PyUpdater supports 3 release channels. Release channels are specified when providing a version number to the --app-version flag. Patches are only created for the stable channel. Examples below.

###Example - Setting channels
Stable:
```
$ pyupdater build --app-version=3.30.1
$ pyupdater build --app-version=2.1
$ pyupdater build --app-version=1.0
```

Beta:
```
$ pyupdater build --app-version=1.0.1b
$ pyupdater build --app-version=3.1b2
$ pyupdater build --app-version=11.3.1beta2
```

Alpha:
```
$ pyupdater build --app-version=1.0.1a
$ pyupdater build --app-version=5.0alpha
$ pyupdater build --app-version=1.1.1alpha1
```

###Example - Update check

Examples below of specifying channels when checking for updates:
```
# Requesting updates from the beta channel
app_update = client.update_check(APP_NAME, APP_VERSION, channel='beta')

# If no channel is specified, stable will be used
app_update = client.update_check(APP_NAME, APP_VERSION)
```

Example of background download:
```
app_update = client.update_check(APP_NAME, APP_VERSION)
if app_update:
    app_update.download(background=True)

# To check the status of the download
# Returns a boolean
app_update.is_downloaded()
```

Examples of setting one or more callbacks. PyUpdater calls set() on the list of plugins to ensure duplicates are not added.
```
# progress hooks get pass a dict with the below keys.
# total: total file size
# downloaded: data received so far
# status: will show either downloading or finished
# percent_complete: Percentage of file downloaded so far
# time: Time left to complete download
def progress(data):
    print('Time remaining'.format(data['time']))

def log_progress(data):
    log.debug('Total file size %s', data['total'])


# You can initialize the client with a callbacks
client = Client(ClientConfig(), progress_hooks=[progress, log_progress])

# Or you can add them later.
client = Client(ClientConfig())
client.add_progress_hook(log_progress)
client.add_progress_hook(progress)
```

###Using basic authentication

Basic authentication is an easy way to prevent unauthorized people from downloading your app from your update server.

Once you've configured your web server to require basic authentication from clients accessing your update repository, modify your update client code like this:
```
headers = urllib3.util.make_headers(basic_auth='username:password')
client = Client(ClientConfig(), headers=headers)
````
Other headers can be sent in the same way, if you want.