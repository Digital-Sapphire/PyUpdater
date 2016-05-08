import logging
from threading import Thread

# Two important imports
from pyupdater import Client
# client_config.py will be written to the root of the dir
# from client_config import ClientConfig


log = logging.getLogger(__name__)


# Example of a client_config.py file
# Will be placed in root of directory
class ClientConfig(object):
    APP_NAME = 'App name'
    COMPANY_NAME = 'Your name or company'
    # Not a real public key
    PUBLIC_KEY = ('dk3lkd8dslk38383lsls8u88sl')
    UPDATE_URLS = ['https://s3-us-west-1.amazonaws.com/ACME',
                   'https://acme.com/updates']


# PyUpdater uses callbacks for download progress
def print_status_info(info):
    # Here you could as the user here if they would
    # like to install the new update and restart
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print downloaded, total, status


# Another callback
def log_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    log.info("%s of %s downloaded - %s", downloaded, total, status)


# Initialize the client
client = Client(ClientConfig())
client.refresh()

# Or initialize & refresh in one step
client = Client(ClientConfig(), refresh=True,
                progress_hook=print_status_info)


# Add as many callbacks as you like
client.add_progress_hook(log_status_info)

# First we check for updates.
# If an update is found an update object will be returned
# If no updates are available, None will be returned
zip_update = client.update_check('7-zip', '0.0.1', channel='beta')

# Example of downloading on the main thread
if zip_update is not None:
    zip_update.download()


# Example of downloading in a thread to not block the main thread
t = Thread(target=zip_update.download)
t.start()


# Install and restart with one method
# Note if your updating a lib this method will not be available
if zip_update is not None and zip_update.is_downloaded():
    zip_update.extract_restart()


# If you want to extract and defer the restart.
if zip_update is not None:
    zip_update.extract()
    # Time passes
    zip_update.restart()
