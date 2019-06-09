# ------------------------------------------------------------------------------
# Copyright (c) 2015-2019 Digital Sapphire
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
from __future__ import unicode_literals


class TConfig(object):
    bad_attr = "bad attr"
    # If left None "Not_So_TUF" will be used
    APP_NAME = "Acme"

    COMPANY_NAME = "Digital"

    DATA_DIR = None

    # Public Key used by your app to verify update data
    # REQUIRED
    PUBLIC_KEY = "rRp4eJzzsPxN1nLXBOuLCqI33HWTridHKJpNnDSUlbU"

    # Online repository where you host your packages
    # and version file
    # REQUIRED
    UPDATE_URLS = ["https://s3-us-west-1.amazonaws.com/pyu-tester/"]
    UPDATE_PATCHES = True

    # Upload Setup
    REMOTE_DIR = None
    HOST = None

    # Tests seem to fail when this is True
    VERIFY_SERVER_CERT = True
