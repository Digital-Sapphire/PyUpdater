import logging
import os
import re
import sys
import tarfile
import zipfile

from dsdev_utils.system import get_system

log = logging.getLogger()

cmd1 = 'pyupdater pkg -P'
cmd2 = 'pyupdater pkg -S'
home_dir = os.path.dirname(os.path.abspath(__file__))


def build(app):
    os.environ['PYINSTALLER_CONFIG_DIR'] = os.path.join(home_dir, '.cache')
    cmd = ('pyupdater build -F --clean --path={} '
           '--app-version={} {}'.format(home_dir, app[1], app[0]))
    os.system(cmd)


def extract(filename):
    ext = os.path.splitext(filename)[1]
    if ext == '.zip':
        archive = zipfile.ZipFile(filename, 'r')
    else:
        archive = tarfile.open(filename, 'r:gz')

    archive.extractall()


def main(use_custom_dir, port):
    scripts = [('app_extract_01.py', '4.1'), ('app_extract_02.py', '4.2')]

    # We use this flag to untar & move our binary to the
    # current working directory
    first = True
    # patch config_file for custom port number
    config_file = open('client_config.py', 'rt').read()
    config_file = re.sub(
            'localhost:\d+', 'localhost:%s' % port, config_file)
    # patch config_file for use_custom_dir
    if use_custom_dir:
        config_file += '\n    USE_CUSTOM_DIR = True\n'
    open('client_config.py', 'wt').write(config_file)
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

            if not os.path.exists(archive_path):
                sys.exit(1)

            # We extract the Acme binary here. When we call pyupdater pkg -P
            # the Acme binary will be moved to the deploy folder. In our test
            # (test_pyupdater.TestExecution.test_execution_update_*) we
            # move all of the files from the deploy directory to the cwd
            # of the test runner.
            extract(archive_path)

            first = False

        os.system(cmd1)

    os.system(cmd2)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: %s <use_custom_dir> <port>' % sys.argv[0])
    else:
        main(sys.argv[1] == 'True', sys.argv[2])
