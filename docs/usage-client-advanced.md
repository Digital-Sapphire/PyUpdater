# Usage | Client | Advanced
PyUpdater supports 3 release channels. Release channels are specified when providing a version number to the --app-version flag. Patches are only created for the stable channel. Examples below.

### Example - Update check

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
# Progress hooks get passed a dict with the below keys.
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

### Using basic authentication

Basic authentication is an easy way to prevent unauthorized people from downloading your app from your update server.

Once you've configured your web server to require basic authentication from clients accessing your update repository, modify your update client code like below.

Other headers can be sent in the same way.
```
headers = {'basic_auth': 'user:pass'}
client = Client(ClientConfig(), headers=headers)
```


### Use your own file downloader
PyUpdater was originally written to work with servers that provide a directory listing.
For services which expose an API to retrieve files, you can use a custom downloader.
Your custom downloader must have the same signature as the MyDownloader class below.

Do note that your file downloader will not always be given a hexdigest kwarg. In those
cases skip hex verification.

```python
from pyupdater.client import Client, DefaultClientConfig


class MyDownloader:

    def __init__(self, filename, urls, **kwargs):
        self.filename = filename
        self.urls = urls
        self.hexdigest = kwargs.get("hexdigest")
        
        self._data = None
    
    def download_verify_return(self):
        # Download the data from the endpoint and return
        return self._data
    
    def download_verify_write(self):
        # Write the downloaded data to the current dir
        try:
            with open(self.filename, 'wb') as f:
                f.write(self._data)
            return True
        except:
            return False

client = Client(DefaultClientConfig(), downloader=MyDownloader)

```
