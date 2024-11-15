import subprocess
from datetime import datetime
from typing import List

_file_date_format = "%Y:%m:%d %H:%M:%S%z"
_original_date_format = "%Y:%m:%d %H:%M:%S.%f%z"
_original_date_format_fallback = "%Y:%m:%d %H:%M:%S.%f"

_date_fields = {
    'file_modification_date/time': [_file_date_format],
    'file_access_date/time': [_file_date_format],
    'file_inode_change_date/time': [_file_date_format],
    'date/time_original': [_original_date_format, _original_date_format_fallback],
    'create_date': [_original_date_format, _original_date_format_fallback],
    'modify_date': [_original_date_format, _original_date_format_fallback],
}

_integer_fields = [
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

_decimal_fields = [
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
    res = subprocess.run(
        ['exiftool', img_file],
        capture_output=True,
        text=True,
    )

    if res.returncode != 0:
        raise Exception(res.stderr)

    exif_metadata = {}

    for line in res.stdout.splitlines():
        parts = line.split(':', 1)
        exif_metadata[parts[0].strip().lower().replace(' ', '_')] = parts[1].strip()

    for (field, date_formats) in _date_fields.items():
        if field in exif_metadata:
            try:
                exif_metadata[field] = _parse_datetime(exif_metadata[field], date_formats)
            except ValueError as e:
                print(f'Failed to convert {field} ({exif_metadata[field]}) to a datetime.')
                raise e

    for field in _integer_fields:
        if field in exif_metadata:
            try:
                exif_metadata[field] = int(exif_metadata[field])
            except ValueError as e:
                print(f'Failed to convert {field} ({exif_metadata[field]}) to an integer.')
                raise e

    for field in _decimal_fields:
        if field in exif_metadata:
            try:
                exif_metadata[field] = float(exif_metadata[field])
            except ValueError as e:
                print(f'Failed to convert {field} ({exif_metadata[field]}) to a float.')
                raise e

    return exif_metadata
