import re

__all__ = (
    'POINT_REGEX',
    'DEFAULT_LATITUDE',
    'DEFAULT_LONGITUDE',
    'DEFAULT_GEO_LOCATION',
)

DEFAULT_LATITUDE = "-90.0"
DEFAULT_LONGITUDE = "-180.0"
POINT_REGEX = re.compile(
    r'POINT\s\('
    r'(?P<lat>[-+]?[0-9]*\.[0-9]+|[0-9]+)'
    r'\s'
    r'(?P<lng>[-+]?[0-9]*\.[0-9]+|[0-9]+)'
    r'\)'
)

DEFAULT_GEO_LOCATION = "POINT({} {})".format(
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE
)
