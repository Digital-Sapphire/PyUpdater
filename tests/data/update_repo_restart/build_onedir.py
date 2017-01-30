import os
import sys
import tarfile
import zipfile

from dsdev_utils.system import get_system

cmd1 = 'pyupdater pkg -P'
cmd2 = 'pyupdater pkg -S'
home_dir = os.path.abspath(__file__)


def build(app):
    cmd = ('pyupdater build -D --path={} '
           '--app-version={} {} --clean'.format(home_dir, app[1], app[0]))
    os.system(cmd)


def extract(filename):
    ext = os.path.splitext(filename)[1]
    if ext == '.zip':
        archive = zipfile.ZipFile(filename, 'r')
    else:
        archive = tarfile.open(filename, 'r:gz')

    archive.extractall()


def main():
    scripts = [('app1.py', '4.1'), ('app2.py', '4.2')]

    # We use this flag to untar & move our binary to the
    # current working directory
    first = True
    for s in scripts:
        build(s)
        if first:
            if sys.platform == 'win32':
                ext = '.zip'
            else:
                ext = '.tar.gz'

            # Build path to archive
            archive_path = os.path.join('pyu-data', 'new',
                                        'Acme-{}-4.1{}'.format(get_system(),
                                                               ext))

            # Will extract contents to cwd
            extract(archive_path)

            first = False

        os.system(cmd1)

    os.system(cmd2)


if __name__ == '__main__':
    main()
