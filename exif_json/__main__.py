import sys

from rich import print

from exif_json import execute_exiftool

if __name__ == '__main__':
    print(execute_exiftool(sys.argv[1]))
