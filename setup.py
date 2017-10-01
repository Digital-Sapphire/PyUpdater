# ------------------------------------------------------------------------------
# Copyright (c) 2015-2017 Digital Sapphire
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
from setuptools import find_packages, setup

import versioneer

KEYWORDS = ('PyUpdater Pyinstaller Auto Update AutoUpdate Auto-Update Esky '
            'updater4pyi bbfreeze ccfreeze freeze cz_freeze')

with open(u'requirements.txt', u'r') as f:
    required = f.read().splitlines()

# ToDo: Remove in PyUpdater 3.0
extra_patch = 'bsdiff4 == 1.1.4'
# End ToDo
extra_s3 = 'PyUpdater-s3-Plugin >= 3.0.6'
extra_scp = 'PyUpdater-scp-Plugin >= 3.0.5'

setup(
    name='PyUpdater',
    version=versioneer.get_version(),
    description='Python Auto Update Library for Pyinstaller',
    author='JMSwag',
    author_email='johnymoswag@gmail.com',
    url='http://www.pyupdater.org',
    download_url=('https://github.com/JMSwag/Py'
                  'Updater/archive/master.zip'),
    license='MIT',
    keywords=KEYWORDS,
    extras_require={
        's3': extra_s3,
        'scp': extra_scp,
        # ToDo: Remove in PyUpdater 3.0
        'patch': extra_patch,
        # End ToDo
        'all': [extra_s3, extra_scp]
    },
    zip_safe=False,
    include_package_data=True,
    tests_require=['pytest'],
    cmdclass=versioneer.get_cmdclass(),
    install_requires=required,
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    pyupdater=pyupdater.cli:main
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'],
)
