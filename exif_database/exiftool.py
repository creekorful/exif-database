"""
exif-database.exiftool: Python wrapper around exiftool(1)
"""

import subprocess
import sys
from datetime import datetime
from typing import List

_FILE_DATE_FORMAT = "%Y:%m:%d %H:%M:%S%z"
_ORIGINAL_DATE_FORMAT = "%Y:%m:%d %H:%M:%S.%f%z"
_ORIGINAL_DATE_FORMAT_FALLBACK = "%Y:%m:%d %H:%M:%S.%f"

_DATE_FIELDS = {
    'file_modification_date/time': [_FILE_DATE_FORMAT],
    'file_access_date/time': [_FILE_DATE_FORMAT],
    'file_inode_change_date/time': [_FILE_DATE_FORMAT],
    'date/time_original': [_ORIGINAL_DATE_FORMAT, _ORIGINAL_DATE_FORMAT_FALLBACK],
    'create_date': [_ORIGINAL_DATE_FORMAT, _ORIGINAL_DATE_FORMAT_FALLBACK],
    'modify_date': [_ORIGINAL_DATE_FORMAT, _ORIGINAL_DATE_FORMAT_FALLBACK],
}

_INTEGER_FIELDS = [
    'image_width',
    'image_height',
    'iso',
    'shutter_count',
    'jpg_from_raw_start',
    'jpg_from_raw_length',
    'thumbnail_offset',
    'thumbnail_length',
    'sr2_sub_ifd_offset',
    'sr2_sub_ifd_length',
    'exif_image_width',
    'exif_image_height',
    'shutter_count_2',
    'sony_iso',
    'iso_auto_min',
    'iso_auto_max',
    'bits_per_sample',
    'strip_byte_counts',
    'rows_per_strip',
    'strip_offsets',
    'x_resolution',
    'y_resolution',
    'samples_per_pixel',
    'sequence_file_number',
    'digital_zoom_ratio',
    'sequence_image_number',
    'focus_position_2',
]

_DECIMAL_FIELDS = [
    'aperture',
    'megapixels',
    'light_value',
    'blue_balance',
    'sony_f_number',
    'sony_max_aperture_value',
    'sony_f_number_2',
    'f_number',
    'max_aperture_value',
    'brightness_value',
    'stops_above_base_iso',
]


def _parse_datetime(raw_value: str, available_formats: List[str]) -> datetime:
    for available_format in available_formats:
        try:
            return datetime.strptime(raw_value, available_format)
        except ValueError:
            continue

    raise ValueError(f"Could not parse datetime '{raw_value}' ({available_formats})")


def execute_exiftool(img_file: str) -> dict:
    """
    Execute exiftool against given image and return results as a dictionary.
    :param img_file: path to image file
    :return: dictionary of exif attributes
    """
    res = subprocess.run(
        ['exiftool', img_file],
        capture_output=True,
        text=True,
        check=True,
    )

    exif_metadata = {}

    for line in res.stdout.splitlines():
        parts = line.split(':', 1)
        exif_metadata[parts[0].strip().lower().replace(' ', '_')] = parts[1].strip()

    for (field, date_formats) in _DATE_FIELDS.items():
        if field in exif_metadata:
            try:
                exif_metadata[field] = _parse_datetime(exif_metadata[field], date_formats)
            except ValueError as e:
                print(f'Failed to convert {field} ({exif_metadata[field]}) to a datetime.')
                raise e

    for field in _INTEGER_FIELDS:
        if field in exif_metadata:
            try:
                exif_metadata[field] = int(exif_metadata[field])
            except ValueError as e:
                print(f'Failed to convert {field} ({exif_metadata[field]}) to an integer.')
                raise e

    for field in _DECIMAL_FIELDS:
        if field in exif_metadata:
            try:
                exif_metadata[field] = float(exif_metadata[field])
            except ValueError as e:
                print(f'Failed to convert {field} ({exif_metadata[field]}) to a float.')
                raise e

    return exif_metadata


if __name__ == '__main__':
    print(execute_exiftool(sys.argv[1]))
