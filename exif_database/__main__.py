import hashlib
import json
import os
import sys
from pathlib import Path

from platformdirs import user_data_dir
from pymongo import MongoClient

from exif_json import execute_exiftool


def _load_pictures_cache() -> dict:
    file_path = _get_make_pictures_cache_path()

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_pictures_cache(pictures: dict):
    file_path = _get_make_pictures_cache_path()

    with open(file_path, 'w') as f:
        json.dump(pictures, f)


def _get_make_pictures_cache_path():
    data_dir = user_data_dir('exif-database', 'creekorful')
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    return os.path.join(data_dir, 'exif-database.json')


if __name__ == '__main__':
    # Authenticate against MongoDB server
    mongo = MongoClient(os.environ['MONGO_URI'])
    database = mongo.exif_database
    collection = database.pictures

    metadata_pictures = []

    # Load saved pictures cache
    saved_pictures = _load_pictures_cache()

    for file in Path(sys.argv[1]).rglob("*.ARW"):
        filename = os.fsdecode(file)

        if filename in saved_pictures:
            print(f'Skipping {filename}')
            continue

        print(f'Uploading {filename}')

        picture_metadata = execute_exiftool(filename)
        metadata_pictures.append(picture_metadata)

        # Append MongoDB identifier
        picture_metadata['_id'] = hashlib.sha1(filename.lower().encode('utf-8')).hexdigest()
        picture_metadata['path'] = filename

        saved_pictures[picture_metadata['path']] = True

    # Insert into MongoDB
    if len(metadata_pictures) > 0:
        collection.insert_many(metadata_pictures)

    # Save saved pictures cache
    _save_pictures_cache(saved_pictures)
