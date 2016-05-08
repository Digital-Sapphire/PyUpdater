from __future__ import unicode_literals
import io
import os
import sys

from jms_utils.system import get_system
import pytest

from pyupdater.builder import ExternalLib
from pyupdater.utils.config import Loader


CONFIG = {
    'APP_NAME': 'PyUpdater Test',
    'COMPANY_NAME': 'ACME',
    'UPDATE_PATCHES': True,

}

if sys.platform == 'win32':
    EXT = '.zip'
else:
    EXT = '.tar.gz'


@pytest.mark.usefixtures("cleandir",)
class TestBuilder(object):

    def test_build(self):
        l = Loader()
        config = l.load_config()
        config.update(CONFIG)
        l.save_config(config)


@pytest.mark.usefixtures("cleandir",)
class TestExternalLib(object):

    def test_archive(self):
        with io.open('test', 'w', encoding='utf-8') as f:
            f.write('this is a test')
        ex = ExternalLib('test2', 'test', '0.1')
        ex.archive()
        assert os.path.exists('test2-{}-0.1{}'.format(get_system(), EXT))


@pytest.mark.usefixtures("cleandir",)
class TestExternalLib2(object):

    def test_archive(self):
        with io.open('test2', 'w', encoding='utf-8') as f:
            f.write('this is a test')
        ex2 = ExternalLib('test', 'test2', '0.2')
        ex2.archive()
        assert os.path.exists('test-{}-0.2{}'.format(get_system(), EXT))
