#Usage | Client | Asset

###Step 1 - Imports & Constants
####client_config.py is written to the root of the repository by default.
```
from pyupdater.client import Client
from client_config import ClientConfig

APP_NAME = 'Super App'
APP_VERSION = '1.1.0'

ASSET_NAME = 'ffmpeg'
ASSET_VERSION = '2.3.2'
```

###Step 2 - Create callback
####This callback will print download progress.
```
def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print downloaded, total, status
```

###Step 3a - Initialize Client
####Initialize client with ClientConfig & later call refresh to get latest update data. You can also add progress hooks later.
```
client = Client(ClientConfig())
client.refresh()

client.add_progress_hook(print_status_info)
```

###Step 3b - Initialize Client Alt
####Initialize client with ClientConfig, add progress hook & refresh during initialization.
```
client = Client(ClientConfig(), refresh=True,
                        progress_hooks=[print_status_info])
```

###Step 4a - Update Check
####update_check returns an LibUpdate object if there is an update available
```
lib_update = client.update_check(ASSET_NAME, ASSET_VERSION)
```

###Step 4b - Update Check Alt
####Checking for updates on the beta channel
```
lib_update = client.update_check(ASSET_NAME, ASSET_VERSION, channel='beta')
```

###Step 5a - Download Update
####If we get an update object we can proceed to download the update.
```
if lib_update is not None:
    lib_update.download()
```

###Step 5b - Download Update Alt
####We can also download in a background thread.
```
if lib_update is not None:
    lib_update.download(background=True)
```

###Step 6a - Extract
####Ensure file downloaded successfully, extract update.

```
if lib_update.is_downloaded():
    lib_update.extract()

# Update will be extracted in the update folder
lib_update.update_folder
```
