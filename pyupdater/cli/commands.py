# ------------------------------------------------------------------------------
# Copyright (c) 2015-2020 Digital Sapphire
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
# ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------
import io
import json
import logging
import os

from dsdev_utils.paths import ChDir, remove_any
from dsdev_utils.terminal import ask_yes_no, get_correct_answer

from pyupdater import __version__, PyUpdater, settings
from pyupdater.cli.helpers import (
    initial_setup,
    print_plugin_settings,
    setup_client_config_path,
    setup_company,
    setup_http_timeout,
    setup_max_download_retries,
    setup_patches,
    setup_plugin,
    setup_urls,
)
from pyupdater.core.key_handler.keys import Keys, KeyImporter
from pyupdater.utils import check_repo, get_http_pool, PluginManager
from pyupdater.utils.builder import Builder, ExternalLib
from pyupdater.utils.config import Config, ConfigManager
from pyupdater.utils.exceptions import UploaderError, UploaderPluginError

log = logging.getLogger(__name__)
CWD = os.getcwd()
# Will get populated by pyupdater.cli
LOG_DIR = None
TEST = False


# A wrapper for _check_repo that will log errors and
# exit the program if needed
def check_repo_ex(exit_on_error=False):
    check = check_repo()
    if check is False:
        log.error("Not a PyUpdater repo: You must initialize " "your repository first")
        if exit_on_error is True and TEST is False:
            os._exit(1)
    return check


# Archive an external asset
def _cmd_archive(*args):  # pragma: no cover
    check_repo_ex(exit_on_error=True)

    log.info("Archiving asset...")
    ns = args[0]
    new_dir = os.path.join(CWD, settings.USER_DATA_FOLDER, "new")
    name = ns.name
    version = ns.version

    with ChDir(new_dir):
        if not os.path.exists(name):
            log.error("%s does not exists", name)
            return
        # Creating a pyupdater compatible archive.
        # See pyupdater.builder for more info.
        ex_lib = ExternalLib(name, version)
        ex_lib.archive()
        if ns.keep is False:
            remove_any(name)
            log.info("Removed: %s", name)
    log.info("Archiving complete")


# Will build and archive an exe from a python script file
def _cmd_build(*args):
    check_repo_ex(exit_on_error=True)

    log.info("Compiling...")
    ns = args[0]
    pyi_args = args[1]
    builder = Builder(ns, pyi_args)
    builder.build()


# Get permission before deleting PyUpdater repo.
def _cmd_clean(*args):  # pragma: no cover
    ns = args[0]
    if ns.yes is True:
        _clean()

    else:
        answer = ask_yes_no(
            "Are you sure you want to remove " "pyupdater data?", default="no"
        )
        if answer is True:
            _clean()
        else:
            log.info("Clean aborted!")


# Remove all traces of PyUpdater from the current repo
def _clean(*args):
    cleaned = False
    # The .pyupdater folder
    if os.path.exists(settings.CONFIG_DATA_FOLDER):
        cleaned = True
        remove_any(settings.CONFIG_DATA_FOLDER)
        log.info("Removed %s folder", settings.CONFIG_DATA_FOLDER)

    # The pyu-data folder
    if os.path.exists(settings.USER_DATA_FOLDER):
        cleaned = True
        remove_any(settings.USER_DATA_FOLDER)
        log.info("Removed %s folder", settings.USER_DATA_FOLDER)

    if cleaned is True:
        log.info("Clean complete...")
    else:
        log.info("Nothing to clean...")


# Just a note: We don't allow changing the app name as this could
# cause issues with updates if not used carefully. If really need
# this value can be changed in the .pyupdater/config.pyu file.
def _cmd_settings(*args):  # pragma: no cover
    check_repo_ex(exit_on_error=True)

    ns = args[0]
    # Used to specify if config needs to be saved
    save_config = True
    cm = ConfigManager()
    config = cm.load_config()

    # Set the path of the client_config.py relative to the root of
    # the repository
    if ns.config_path is True:
        setup_client_config_path(config)

    # Change the company name. This will effect the file path on the end users
    # computer to place update files & meta data
    if ns.company is True:
        setup_company(config)

    # The amount of times the client retries downloads
    if ns.max_download_retries is True:
        setup_max_download_retries(config)

    # The http timeout for FileDownloader
    if ns.http_timeout is True:
        setup_http_timeout(config)

    # Base urls to online updates & meta data
    if ns.urls is True:
        setup_urls(config)

    # Enable/Disable binary patches
    if ns.patches is True:
        setup_patches(config)

    # Setup config for requested upload plugin
    if ns.plugin is not None:
        setup_plugin(ns.plugin, config)

    # Show list of installed upload plugins
    if ns.show_plugin is not None:
        save_config = False
        print_plugin_settings(ns.show_plugin, config)

    # If any changes have been made, save data to disk.
    if save_config is True:
        cm.save_config(config)
        log.info("Saved config")


# Initialize PyUpdater repo
def _cmd_init(*args):  # pragma: no cover
    if not os.path.exists(
        os.path.join(settings.CONFIG_DATA_FOLDER, settings.CONFIG_FILE_USER)
    ):
        # Load a basic config.
        config = Config()

        # Run config through all of the setup functions
        config = initial_setup(config)
        log.info("Creating pyu-data dir...")

        # Initialize PyUpdater with newly created config
        pyu = PyUpdater(config)

        # Setup repository
        pyu.setup()

        # Load config manager & save config to disk
        cm = ConfigManager()
        cm.save_config(config)
        log.info("Setup complete")
    else:
        log.error("Not an empty PyUpdater repository")


# We create and import keys with this puppy.
def _cmd_keys(*args):  # pragma: no cover
    check = check_repo_ex()

    ns = args[0]
    # We try to prevent developers from creating root keys on the dev
    # machines.
    if ns.create_keys is True and ns.import_keys is True:
        log.error("Only one options is allowed at a time")
        return

    # Okay the actual check is pretty weak but we are all grown ups here :)
    if ns.create_keys is True and check is True:
        log.error("You can not create off-line keys on your dev machine")
        return

    # Can't import if we don't have a config to place it in.
    if ns.import_keys is True and check is False:
        return

    # We are supposed to be on another secure computer.
    # Security is in the eye of the beholder.
    # That was deep.
    if ns.create_keys is True and check is False:
        if hasattr(ns, "test"):
            log.debug("We are testing!")
            app_name = "test"
            # Starting up with some testing in mind.
            k = Keys(test=True)
        else:
            k = Keys()
            # Get the app name for the soon to be generated keypack.pyu
            app_name = get_correct_answer("Please enter app name", required=True)

        # Create the keypack for this particular application.
        # make_keypack will return True if successful.
        if k.make_keypack(app_name):
            log.info("Keypack placed in cwd")
        else:
            log.error("Failed to create keypack")
            return

    # Save the keypack.pyu that's in the current directory to the
    # .pyupdater/config.pyu file.
    if ns.import_keys is True and check is True:
        cm = ConfigManager()
        config = cm.load_config()
        ki = KeyImporter()
        if ki.start():
            log.info("Keypack import successfully")
            cm.save_config(config)
        else:
            log.error("Keypack import failed")


# Create a spec_file and place it in the cwd.
# This will be used when the application being build goes a little
# beyond the basics. This is good!
def _cmd_make_spec(*args):
    check_repo_ex(exit_on_error=True)

    ns = args[0]
    pyi_args = args[1]
    builder = Builder(ns, pyi_args)
    builder.make_spec()
    log.info("Spec file placed in cwd")


# The pkg command will move, gather meta-data & sign all
# packages within the pyu-data folder
def _cmd_pkg(*args):
    check_repo_ex(exit_on_error=True)

    ns = args[0]
    cm = ConfigManager()
    pyu = PyUpdater(cm.load_config())

    # Please give pkg something to do
    if ns.process is False and ns.sign is False:
        log.error("You must specify a command")
        return

    # Gather meta data and save to disk
    if ns.process is True:
        log.info("Processing packages...")
        pyu.process_packages(ns.verbose)
        log.info("Processing packages complete")

    # Sign the update meta-data with the repo private key.
    if ns.sign is True:
        log.info("Signing packages...")
        pyu.sign_update(ns.split_version)
        log.info("Signing packages complete")


# Uploads the debug logs to a private github gist
def _cmd_collect_debug_info(*args):  # pragma: no cover
    log.info("Starting log export")

    # A helper function that adds the filename & data to the
    # payload in preparation for upload.
    def _add_file(payload, filename):
        with io.open(filename, "r", encoding="utf-8") as f:
            data = f.read()
        payload["files"][filename] = {"content": data}

    # A helper function that uploads the data to a private gist.
    def _upload(data):
        api = "https://api.github.com/"
        gist_url = api + "gists"
        http = get_http_pool()
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PyUpdater",
        }

        r = http.urlopen("POST", gist_url, headers=headers, body=json.dumps(data))
        try:
            data = json.loads(r.data)
            url = data["html_url"]
        except Exception as err:
            log.debug(err, exc_info=True)
            log.debug(json.dumps(r.data, indent=2))
            url = None
        return url

    # Payload skeleton per githubs specification.
    # https://developer.github.com/v3/gists/
    upload_data = {"files": {}, "description": "PyUpdater debug logs", "public": False}

    if LOG_DIR is None:
        log.error("LOG_DIR is not set")
        return

    with ChDir(LOG_DIR):
        # Get a list of all files in the log directory.
        temp_files = os.listdir(os.getcwd())

        # Exited quickly if no files present.
        if len(temp_files) == 0:
            log.info("No log files to collect")
            return

        log.info("Collecting logs")
        for t in temp_files:
            # If the file matches the base name add it to the payload
            if t.startswith(settings.LOG_FILENAME_DEBUG):
                log.debug("Adding %s to log", t)
                _add_file(upload_data, t)

    log.info("Uploading collected logs")
    # Attempt upload of debug files.
    url = _upload(upload_data)

    if url is None:
        log.error("Could not upload debug info to github")
    else:
        log.info("Log export complete: %s", url)


# Show list of installed upload plugins
def _cmd_plugins(*args):
    plug_mgr = PluginManager({})
    # Doing some basic formatting. Design help here would be appreciated.
    # By the way I just want to thank all the contributors and bug submitters.
    names = ["\n"]
    for n in plug_mgr.get_plugin_names():
        out = "{} by {}\n".format(n["name"], n["author"])
        names.append(out)
    output = "".join(names)
    log.info("Upload plugins:%s", output)


# Upload the assets with the requested upload plugin
def _cmd_upload(*args):  # pragma: no cover
    check_repo_ex(exit_on_error=True)

    ns = args[0]

    # The upload plugin requested
    upload_service = ns.service

    # We need something to work with
    if upload_service is None:
        log.error("Must provide service name")
        return

    cm = ConfigManager()
    pyu = PyUpdater(cm.load_config())
    try:
        # Configure PyUpdater to use the requested upload plugin
        pyu.set_uploader(upload_service, ns.keep)
    # Something happened during uploading
    except UploaderError as err:
        log.error(err)
        return
    # Something happened with the upload plugin
    except UploaderPluginError as err:
        log.debug(err)
        log.error("Invalid upload plugin")
        log.error('Use "pyupdater plugins" to get a ' "list of installed plugins")
        return

    # Try to upload the files in the deploy directory. Get it...
    # In all seriousness, I really want this to go smoothly.
    log.info("Starting upload")
    try:
        complete = pyu.upload()
    except Exception as err:
        complete = False
        log.debug(err, exc_info=True)
        log.error(err)

    if complete:
        print("")
        log.info("Upload successful")
    else:
        log.error("Upload failed!")


# Print the version of PyUpdater to the console.
def _cmd_version(*args):
    print("PyUpdater {}".format(__version__))
