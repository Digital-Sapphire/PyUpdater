# Migrate from Esky

Currently the best way to migrate from Esky is follow the [Getting Started](usage-cli.md) guide.
End Users will have to download this, updated version of your app, directly from a download link.

### Migration Help

##### Configuration

Esky:
    
  - Uses setup.py

PyUpdater:

  - Set during repository initialization.


##### Parsing App Current Versions

Esky:

  - Parses local repository.

PyUpdater:

  - Version is set within application script.


##### Parsing App Update Versions

Esky:

  - Parses update repository.

PyUpdater:

  - Uses a dedicated version file which includes hashes for security and integrity.


##### App Update Process

Esky:

  - Initialize Esky update client, then  use update method.

PyUpdater:

  - Initialize PyUpdater client, then use update method.