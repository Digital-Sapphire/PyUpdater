from __future__ import print_function
from __future__ import unicode_literals

import shutil
import os

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


print('Start dir: {}'.format(HOME))


def check_x(x):

    def bad_file(f):
        ext = os.path.splitext(f)[1]
        if ext == '.pyc':
            return True
        return False

    def bad_dir(d):
        bad = ['__pycache__', 'htmlcov', 'build',
               'dist', 'PyUpdater.egg-info']
        if os.path.basename(d) in bad:
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
        print('Removed {}'.format(x))


def main():
    for root, dirs, files in os.walk(HOME):
        for f in files:
            path = os.path.abspath(os.path.join(root, f))
            check_x(path)
        for d in dirs:
            path = os.path.abspath(os.path.join(root, d))
            check_x(path)


if __name__ == '__main__':
    main()
