## Demos
PyUpdater make heavy use of the pyi-data folder.

####Steps

######1. Have your configuration file set
[Click Here](http://docs.pyupdater.org/configuration.php "Example Usage") for configuration options

######2. Build your app:

    $ pyupdater build app.py --app-name=APP --app-version=0.1.0


######3. Use PackageHandler's process_packages method. Will move copy app updates to version folder in the files dir & also move udpate form new folder to deploy folder

######4. Now use KeyHanlder sign_update method to add a signature to the version file & copies it to the deploy dir.
