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
from __future__ import print_function

import os
import shutil

from dsdev_utils.paths import ChDir, remove_any

HTML_DIR = os.path.join(os.getcwd(), "site")
DEST_DIR = os.path.join(
    os.path.expanduser("~"), "src", "Web", "PyUpdater", "public_html"
)


def main():
    with ChDir(DEST_DIR):
        files = os.listdir(os.getcwd())
        for f in files:
            remove_any(f)

    with ChDir(HTML_DIR):
        files = os.listdir(os.getcwd())
        for f in files:
            if f.startswith(u"."):
                continue
            if f.startswith("__init__"):
                continue
            if os.path.isfile(f):
                shutil.copy(f, os.path.join(DEST_DIR, f))
            elif os.path.isdir(f):
                shutil.copytree(f, DEST_DIR + os.sep + f)

    shutil.rmtree(HTML_DIR)


if __name__ == "__main__":
    main()
    print(u"Move complete")
