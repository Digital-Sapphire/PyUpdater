from setuptools import find_packages, setup

import versioneer


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
    description='Simple App update framwork',
    author='Johny Mo Swag',
    author_email='johnymoswag@gmail.com',
    url='http://www.pyupdater.org',
    download_url=('https://github.com/JMSwag/Py'
                  'Updater/archive/master.zip'),
    license='MIT',
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
