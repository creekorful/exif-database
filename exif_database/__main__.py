import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from pymongo import MongoClient


def _execute_exiftool(img_file: str) -> dict:
    res = subprocess.run(
        ['exiftool', img_file],
        capture_output=True,
        text=True,
    )

    exif_metadata = {}

    for line in res.stdout.splitlines():
        parts = line.split(':', 1)
        exif_metadata[parts[0].strip().lower().replace(' ', '_')] = parts[1].strip()

    return exif_metadata


if __name__ == '__main__':
    # Authenticate against MongoDB server
    mongo = MongoClient(os.environ['MONGO_URI'])
    database = mongo.exif_database
    collection = database.pictures

    metadata_pictures = []

    # Load saved pictures cache
    try:
        with open('exif-database.json', 'r') as f:
            saved_pictures = json.load(f)
    except FileNotFoundError:
        saved_pictures = {}

    for file in Path(sys.argv[1]).rglob("*.ARW"):
        filename = os.fsdecode(file)

        if filename in saved_pictures:
            print(f'Skipping {filename}')
            continue

        print(f'Uploading {filename}')

        picture_metadata = _execute_exiftool(filename)
        metadata_pictures.append(picture_metadata)

        # Append MongoDB identifier
        picture_metadata['_id'] = hashlib.sha1(filename.lower().encode('utf-8')).hexdigest()
        picture_metadata['path'] = filename

        saved_pictures[picture_metadata['path']] = True

    # Insert into MongoDB
    collection.insert_many(metadata_pictures)

    # Save saved pictures cache
    with open('exif-database.json', 'w') as f:
        json.dump(saved_pictures, f)
