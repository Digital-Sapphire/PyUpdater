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
from setuptools import find_packages, setup

import versioneer

KEYWORDS = (
    "PyUpdater Pyinstaller Auto Update AutoUpdate Auto-Update Esky "
    "updater4pyi bbfreeze ccfreeze freeze cz_freeze pyupdate"
)


with open(u"requirements.txt", u"r") as f:
    required = f.read().splitlines()


with open("README.md", "r") as f:
    readme = f.read()


extra_s3 = "PyUpdater-s3-Plugin >= 4.0.5"
extra_scp = "PyUpdater-scp-Plugin >= 4.0"


setup(
    name="PyUpdater",
    version=versioneer.get_version(),
    description="Python Auto Update Library for Pyinstaller",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Digital Sapphire",
    author_email="oss@digitalsapphire.io",
    url="https://www.pyupdater.org",
    download_url=("https://github.com/Digital-Sapphire/PyUpdater/archive/master.zip"),
    license="MIT",
    keywords=KEYWORDS,
    extras_require={"s3": extra_s3, "scp": extra_scp, "all": [extra_s3, extra_scp]},
    zip_safe=False,
    include_package_data=True,
    tests_require=["pytest"],
    cmdclass=versioneer.get_cmdclass(),
    install_requires=required,
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    pyupdater=pyupdater.cli:main
    """,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
