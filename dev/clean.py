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
import shutil
import os

# If clean.py is moved from dev dir please update
HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


print("Start dir: {}".format(HOME))


def check_x(x):
    def bad_file(f):
        ext = os.path.splitext(f)[1]
        if ext == ".pyc":
            return True
        basename = os.path.basename(f)
        if basename.startswith(".coverage."):
            return True
        return False

    def bad_dir(d):
        basename = os.path.basename(d)
        bad = ["__pycache__", "htmlcov", "build", "dist", "PyUpdater.egg-info"]
        if basename in bad:
            return True
        return False

    if os.path.isfile(x):
        if bad_file(x) is True:
            remove(x)
    if os.path.isdir(x):
        if bad_dir(x) is True:
            remove(x)


def remove(x):
    removed = False
    if os.path.isfile(x):
        removed = True
        os.remove(x)
    if os.path.isdir(x):
        removed = True
        shutil.rmtree(x, ignore_errors=True)
    if removed is True:
        print("Removed {}".format(x))


def main():
    for root, dirs, files in os.walk(HOME):
        for f in files:
            path = os.path.abspath(os.path.join(root, f))
            check_x(path)
        for d in dirs:
            path = os.path.abspath(os.path.join(root, d))
            check_x(path)


if __name__ == "__main__":
    main()
