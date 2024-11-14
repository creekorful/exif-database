import subprocess
from datetime import datetime

_file_date_format = "%Y:%m:%d %H:%M:%S%z"
_original_date_format = "%Y:%m:%d %H:%M:%S.%f%z"


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

    # Handle dates
    date_fields = {
        'file_modification_date/time': _file_date_format,
        'file_access_date/time': _file_date_format,
        'file_inode_change_date/time': _file_date_format,
        'date/time_original': _original_date_format,
        'create_date': _original_date_format,
    }

    for (date_field, date_format) in date_fields.items():
        if date_field in exif_metadata:
            exif_metadata[date_field] = datetime.strptime(exif_metadata[date_field], date_format)

    return exif_metadata
