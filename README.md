# exif-database

Dump pictures metadata into a MongoDB database for statistics purpose

## How does it work?

This script works by scanning all files in given directory and then serialize the EXIF metadata to push them
into a MongoDB instances.

## Installation

This package is available on PyPi. You can install it using pip.

```
$ pip install exif-database
```

## Configuration

No configuration is needed. You only need to set up a MongoDB server with a dedicated collection and user
in order for the script to save the data.

[More information](https://docs.bitnami.com/aws/infrastructure/mean/configuration/create-database/).

Note: A docker compose file is provided with this repository but is only used to set up a dev environment easily.

## Executing the script(s)

This package provides two binaries:

### exif-database

This is the main binary, the one used to parse the EXIF and send them to MongoDB.

```
$ MONGO_URI=mongodb://user:pass@server/db python3 -m exif_database <path to images dir>
```

### exif-database.exiftool

This tool parse EXIF metadata of given file and output them to stdout.

```
$ python3 -m exif_database.exiftool <path to image file>
```