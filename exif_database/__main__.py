import hashlib
import json
import os
import sys
from pathlib import Path

from platformdirs import user_data_dir
from pymongo import MongoClient

from exif_json import execute_exiftool

_allowed_extensions = [
    '.ARW',
    '.NEF',
]


def _load_pictures_cache() -> dict:
    _file_path = _get_make_pictures_cache_path()

    try:
        with open(_file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_pictures_cache(_pictures: dict):
    _file_path = _get_make_pictures_cache_path()

    with open(_file_path, 'w') as f:
        json.dump(_pictures, f)


def _get_make_pictures_cache_path():
    _data_dir = user_data_dir('exif-database', 'creekorful')
    Path(_data_dir).mkdir(parents=True, exist_ok=True)

    return os.path.join(_data_dir, 'exif-database.json')


def _is_extension_allowed(_filename: str) -> bool:
    for _allowed_extension in _allowed_extensions:
        if _filename.endswith(_allowed_extension):
            return True

    return False


if __name__ == '__main__':
    # Authenticate against MongoDB server
    mongo = MongoClient(os.environ['MONGO_URI'])
    database = mongo.exif_metadata
    collection = database.pictures

    metadata_pictures = []

    # Load saved pictures cache
    saved_pictures = _load_pictures_cache()

    # Keep track of processed pictures
    processed_pictures = 0
    max_processed_pictures = None if len(sys.argv) < 3 else int(sys.argv[2])

    for file in Path(sys.argv[1]).rglob("*.*"):
        filename = os.fsdecode(file)

        if not _is_extension_allowed(filename):
            continue

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

        processed_pictures = processed_pictures + 1

        if max_processed_pictures is not None and processed_pictures >= max_processed_pictures:
            break

    # Insert into MongoDB
    if len(metadata_pictures) > 0:
        collection.insert_many(metadata_pictures)

    # Save saved pictures cache
    _save_pictures_cache(saved_pictures)
