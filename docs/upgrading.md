#Upgrading
#####Note: Major version will maintain compatibility.

##To Version 2.0
###Coming from PyUpdater < 1.1
1. You'll need to update to PyUpdater 1.1.15
2. If using progress hooks note that progress_hook changed to progress_hooks and only accepts lists
3. Release a new version of your application that uses PyUpdater 1.1.15
4. Ensure all end users are using the latest version of your application.
5. Once all of your end users have the latest version or your application, you can upgrade to PyUpdater 2.0

This extra step is required because the schema of the version manifest file changed to support release channels. Version 1.1 was release about 7+ months ago. In the future I'll mention when I'm adding backwards compatibility code which is marked for deprecation.