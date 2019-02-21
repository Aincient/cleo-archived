import json
import glob
import os

from bs4 import BeautifulSoup

from xml.etree.ElementTree import fromstring

from django.conf import settings

import requests

from six import PY3
from six.moves import urllib
from six.moves.urllib.parse import urlparse

from xmljson import badgerfish as bf

from .conf import MUSES_IMPORTERS_RMO_NL_IMAGES_BASE_PATH

__all__ = (
    'extract_filename_from_url',
    'save_image',
    'NationalMuseumOfAntiquitiesClient',
)


def extract_filename_from_url(url):
    """Extract filename from URL.

    :param url:
    :return:
    """
    result = urlparse(url)
    return os.path.basename(result.path)


def save_image(url):
    """Save image locally.

    :param url:
    :return:
    """
    basename = extract_filename_from_url(url)
    filename = os.path.join(
        MUSES_IMPORTERS_RMO_NL_IMAGES_BASE_PATH,
        basename
    )
    if PY3:
        urllib.request.urlretrieve(url, filename)
    else:
        urllib.urlretrieve(url, filename)
    return filename


class NationalMuseumOfAntiquitiesClient(object):
    """NationalMuseumOfAntiquities (rmo.nl) API client."""

    def __init__(self, url=None, tmp_dir=None):
        """Constructor.

        :param url: Search URL.
        :param tmp_dir: Temporary directory to store JSON files.
        :type url: str
        :type tmp_dir: str
        """
        self.url = url
        self.tmp_dir = tmp_dir

    def configure_from_settings(self):
        """Configure from settings.

        :return:
        """
        config = settings.MUSES_CONFIG['importers']['rmo_nl']
        self.url = config['url']
        self.tmp_dir = config['tmp_dir']

    def get_object_list(self):
        """Fetch API objects and dump results into the JSON files.

        - Fetches objects list (starting from the given offset).
        - Stores the fetched objects locally in the directory specified.

        :param page:
        :return:
        """
        url = self.url[:]
        response = requests.get(url)
        if response.ok:
            raw_data = response.text.encode('utf-8')
            xml_data = BeautifulSoup(raw_data, 'lxml-xml')
            items = xml_data.find_all('RMO_XML')
            json_data = []
            for item in items:
                json_data.append(
                    bf.data(fromstring(str(item)))['RMO_XML']
                )

            with open(
                    os.path.join(
                        self.tmp_dir,
                        'objects',
                        'rmo_all.json'
                    ),
                    'w'
            ) as tmp_file:
                json.dump(json_data, tmp_file, ensure_ascii=False)

    def load_objects_from_json_cache(self):
        """Load objects from JSON cache.

        :return:
        """
        objects = []
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'objects', 'rmo_all.json')
        ):
            with open(filename, 'r') as json_file:
                json_data = json.load(json_file)
                objects += json_data
        return objects
