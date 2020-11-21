# Usage | CLI | Advanced
PyUpdater supports 3 release channels. Release channels are specified when providing a version number to the --app-version flag. Patches are created for each channel. Examples below.

### Example - Setting channels
Stable:
```
$ pyupdater build --app-version=3.30.1
$ pyupdater build --app-version=2.1
$ pyupdater build --app-version=1.0
```

Beta:
```
$ pyupdater build --app-version=1.0.1b
$ pyupdater build --app-version=3.1b2
$ pyupdater build --app-version=11.3.1beta2
```

Alpha:
```
$ pyupdater build --app-version=1.0.1a
$ pyupdater build --app-version=5.0alpha
$ pyupdater build --app-version=1.1.1alpha1
```