import logging
import os

from stevedore.extension import ExtensionManager

log = logging.getLogger()
log.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
log.addHandler(sh)

namespace = 'pyu.uploaders'


def upgrade_pip():
    command = "./update.sh"
    log.debug("command: %s", command)
    os.system(command)


def main():
    # upgrade_pip()
    mgr = ExtensionManager(namespace)
    eps = mgr.ENTRY_POINT_CACHE
    log.debug('EP Cache: %s', eps)

    for ep in eps[namespace]:
        try:
            ep.load()
            log.info("Successful Plugin Load")
        except Exception as err:
            log.error(str(err), exc_info=True)

    log.info("Test Complete")


main()
