# Usage | CLI | Assets

### Step 1 - Prepare external asset

Place asset in pyu-data/new directory

### Step 2 - Run archive command
```
$ pyupdater archive --name example.so --version 0.1.0
```

### Step 3 - Create patches

Time to create binary patches if enabled, add sha256 hashes to version manifest & copy files to deploy folder. You can combine --process with --sign.
```
$ pyupdater pkg --process
```

### Step 4 - Cryptographically Sign

Now lets sign our version manifest file, gzip our version manifest, gzip keyfile & place in the deploy directory. You can combine --sign with --process
```
$ pyupdater pkg --sign
```

### Step 5 - List Installed Plugins

Get a list of the plugins you have installed. You probably wont have to run this many times :)
```
# You can install the official plugins with
# pip install pyupdater[s3, scp]
$ pyupdater plugins

s3 by Digital Sapphire
scp by Digital Sapphire

```

### Step 6 - Configure Plugin

Your plugin may or may not need configuration. If you are not sure then go ahead and check. It won't hurt anything. If nothing happens then the coast is clear. Plugin authors may ask you to set env vars. Please consult their docs. Now off we go.
```
$ pyupdater settings --plugin s3
```

### Step 7 - Upload

We've made it. Time to upload our updates, patches & metadata. On the first run you will not have any patches. There's no src files yet. It'll happen on the next build.
```
$ pyupdater upload --service s3
```
