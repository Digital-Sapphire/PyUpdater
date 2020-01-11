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
import logging
import os
import sys

from dsdev_utils import terminal

from pyupdater import settings
from pyupdater.utils import PluginManager

log = logging.getLevelName(__name__)


def print_plugin_settings(plugin_name, config):  # pragma: no cover
    pm = PluginManager(config)
    config = pm.get_plugin_settings(plugin_name)
    if len(config.keys()) == 0:
        print("No config found for {}".format(plugin_name))
    else:
        print(plugin_name)
        print(config)


def setup_appname(config):  # pragma: no cover
    if config.APP_NAME is not None:
        default = config.APP_NAME
    else:
        default = None
    config.APP_NAME = terminal.get_correct_answer(
        "Please enter app name", required=True, default=default
    )


def setup_client_config_path(config):  # pragma: no cover
    _default_dir = os.path.basename(os.path.abspath(os.getcwd()))
    question = (
        "Please enter the path to where pyupdater "
        "will write the client_config.py file. "
        "You'll need to import this file to "
        "initialize the update process. \nExamples:\n\n"
        "lib/utils, src/lib, src. \n\nLeave blank to use "
        "the current directory"
    )
    answer = terminal.get_correct_answer(question, default=_default_dir)

    if answer == _default_dir:
        config.CLIENT_CONFIG_PATH = settings.DEFAULT_CLIENT_CONFIG
    else:
        answer = answer.split(os.sep)
        answer.append(settings.DEFAULT_CLIENT_CONFIG[0])

        config.CLIENT_CONFIG_PATH = answer


def setup_company(config):  # pragma: no cover
    if config.COMPANY_NAME is not None:
        default = config.COMPANY_NAME
    else:
        default = None
    temp = terminal.get_correct_answer(
        "Please enter your name or company name", required=True, default=default
    )
    config.COMPANY_NAME = temp


def setup_max_download_retries(config):  # pragma: no cover
    default = config.MAX_DOWNLOAD_RETRIES
    while 1:
        temp = terminal.get_correct_answer(
            "Enter max download retries", required=True, default=str(default)
        )
        try:
            temp = int(temp)
        except Exception as err:
            log.error(err)
            log.debug(err, exc_info=True)
            continue

        if temp > 10 or temp < 1:
            log.error("Max retries can only be from 1 to 10")
            continue
        break

    config.MAX_DOWNLOAD_RETRIES = temp


def setup_http_timeout(config):  # pragma: no cover
    default = config.HTTP_TIMEOUT
    while 1:
        temp = terminal.get_correct_answer(
            "Enter HTTP timeout in seconds", required=True, default=str(default)
        )
        try:
            temp = int(temp)
        except Exception as err:
            log.error(err)
            continue

        if temp < 1:
            log.error("HTTP timeout has to be >= 1")
            continue
        break

    config.HTTP_TIMEOUT = temp


def setup_patches(config):  # pragma: no cover
    question = "Would you like to enable patch updates?"
    config.UPDATE_PATCHES = terminal.ask_yes_no(question, default="yes")


def setup_plugin(name, config):  # pragma: no cover
    pgm = PluginManager(config)
    plugin = pgm.get_plugin(name)
    if plugin is None:
        sys.exit("Invalid plugin name...")

    pgm.config_plugin(name, config)


def setup_urls(config):  # pragma: no cover
    url = terminal.get_correct_answer("Enter a url to ping for updates.", required=True)
    config.UPDATE_URLS = [url]
    while 1:
        answer = terminal.ask_yes_no(
            "Would you like to add " "another url for backup?", default="no"
        )
        if answer is True:
            url = terminal.get_correct_answer("Enter another url.", required=True)
            config.UPDATE_URLS.append(url)
        else:
            break


def initial_setup(config):  # pragma: no cover
    setup_appname(config)
    setup_company(config)
    setup_urls(config)
    setup_patches(config)
    setup_client_config_path(config)
    return config
