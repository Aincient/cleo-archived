from collections import defaultdict
import csv
import json
import glob
import logging
import os
import re

from django.conf import settings

import tablib
import requests

from six import PY3
from six.moves import urllib
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import urljoin

from ...phantomjs_helpers import phantom_js_get
from .conf import MUSES_IMPORTERS_METMUSEUM_ORG_IMAGES_BASE_PATH

__all__ = (
    'MetropolitanClient',
    'extract_filename_from_url',
    'fetch_api_data_defaults',
    'save_image',
)

LOGGER = logging.getLogger(__name__)

IMAGES_FILE_PATTERN = re.compile(r'^met_images(\d+)\.json$')


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
        MUSES_IMPORTERS_METMUSEUM_ORG_IMAGES_BASE_PATH,
        basename
    )
    if PY3:
        urllib.request.urlretrieve(url, filename)
    else:
        urllib.urlretrieve(url, filename)
    return filename


class FatalError(Exception):
    """Fatal error."""


class MetropolitanClient(object):
    """Metropolitan API client."""

    def __init__(self,
                 tmp_dir=None,
                 object_list_url=None,
                 object_images_url=None):
        """Constructor.

        :param tmp_dir: Temporary directory to store JSON files.
        :param object_list_url:
        :param object_images_url:
        :type tmp_dir: str
        :type object_list_url: str
        :type object_images_url: str
        """
        self.auth_headers = {}
        self.tmp_dir = tmp_dir
        self.object_list_url = object_list_url
        self.object_images_url = object_images_url
        if self.tmp_dir:
            self.object_list_filename = os.path.join(
                self.tmp_dir,
                'objects',
                'MetObjects.csv'
            )
        else:
            self.object_list_filename = None

    def configure_from_settings(self):
        """Configure from settings.

        :return:
        """
        config = settings.MUSES_CONFIG['importers']['metmuseum_org']
        self.object_list_url = config['object_list_url']
        self.object_images_url = config['object_images_url']
        self.tmp_dir = config['tmp_dir']
        self.object_list_filename = os.path.join(
            self.tmp_dir,
            'objects',
            'MetObjects.csv'
        )

    def download_objects_list(self):
        """Download objects list.

        :return:
        """
        if PY3:
            urllib.request.urlretrieve(
                self.object_list_url,
                self.object_list_filename
            )
        else:
            urllib.urlretrieve(
                self.object_list_url,
                self.object_list_filename
            )

    def get_object_list(self, offset):
        """Fetch API objects and dump results into the JSON files.

        - Fetches objects list (starting from the given offset).
        - Stores the fetched objects locally in the directory specified.

        :param offset:
        :return:
        """
        if not offset:
            offset = 0

        data = []
        json_dict = {}

        csv_data = open(self.object_list_filename).read()
        data = tablib.Dataset().load(csv_data)
        data.headers[0] = data.headers[0].replace('\ufeff', '')
        json_data = json.loads(data.export('json'))
        # for obj in json_data:
        #     json_dict[obj['Object ID']] = obj
        json_dict = self.filter_objects(json_data)
        self.write_objects_to_json_cache(json_dict)

        return json_data

    def filter_objects(self, objects):
        """Filter objects list by folder value.

        :param objects:
        :param folder_value:
        :type objects: list
        :type folder_value: str
        :return:
        :rtype: dict
        """
        # We need to make sure we have unique results and having a dict is
        # often handy.
        filtered_objects = {}

        for obj in objects:
            object_number = obj.pop('\ufeffObject Number', None)
            if object_number:
                obj['Object Number'] = object_number
            if obj['Department'] == 'Egyptian Art':
                filtered_objects.update({obj['Object ID']: obj})

        return filtered_objects

    def write_objects_to_json_cache(self, data):
        """Write data.

        :param data:
        :return:
        """
        with open(
                os.path.join(
                    self.tmp_dir,
                    'objects',
                    'met.json'
                ),
                'w'
        ) as tmp_file:
            json.dump(data, tmp_file, ensure_ascii=False)

    def load_objects_from_json_cache(self):
        """Load objects from JSON cache.

        :return:
        """
        data = {}
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'objects', 'met*.json')
        ):
            with open(filename, 'r') as json_file:
                data.update(json.load(json_file))
        return data

    def load_object_ids_from_json_cache(self, parse_to_int=False):
        """Load object IDs from JSON cache.

        :return:
        """
        ids = []
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'objects', 'met.json')
        ):
            with open(filename, 'r') as json_file:
                json_data = json.load(json_file)
                ids = list(json_data.keys())

        if parse_to_int:
            ids = [int(_id) for _id in ids]

        return ids

    def get_object_images(self, object_id):
        """Get object image.

        :param object_id: ID of the object for which we try to retrieve the
                          image.
        :type object_id: int
        :return:
        """
        filename = os.path.join(
            self.tmp_dir,
            'images',
            'met_images{}.json'.format(object_id)
        )
        if not os.path.isfile(filename):
            LOGGER.info("Importing images for {}".format(object_id))
            url = self.object_images_url.format(object_id)
            result = phantom_js_get(url)

            if 'results' in result and result['results']:
                with open(filename, 'w') as tmp_file:
                    json.dump(result['results'], tmp_file, ensure_ascii=False)
                return result['results']
        else:
            LOGGER.info("Skipping for {}".format(object_id))

    def get_object_list_images(self, object_ids, continue_from_id=None):
        """Get all images for the given object list.

        :param object_ids: List of object IDs.
        :type object_ids: list
        :return:
        """
        data = {}
        object_ids = sorted(object_ids)
        for object_id in object_ids:
            # Continue
            if continue_from_id is not None:
                if int(object_id) < continue_from_id:
                    continue

            image_data = self.get_object_images(object_id)
            if image_data:
                data.update({object_id: image_data})
        return data

    def get_object_list_images_from_json_cache(self):
        """Get all images for objects stored in cache.

        Note, that in this case images are not yet stored in the cache.
        We're using the objects from cache using
        :meth:`load_object_ids_from_json_cache`.

        :return:
        """
        object_ids = self.load_object_ids_from_json_cache()
        return self.get_object_list_images(object_ids)

    def load_object_list_images_from_json_cache(self):
        """Load images stored in JSON cache.

        :return:
        """
        objects = {}
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'images', 'met_images*.json')
        ):
            with open(filename, 'r') as json_file:
                base_filename = os.path.basename(filename)
                object_id = \
                    re.match(IMAGES_FILE_PATTERN, base_filename).group(1)
                json_data = json.load(json_file)
                objects.update({object_id: json_data})
        return objects

    def write_object_images_to_json_cache(self, data):
        """Write item images to JSON cache.

        This produces a single file. It's supposed to be used when making
        tricks with locally stored images.

        :param data:
        :return:
        """
        with open(
            os.path.join(
                self.tmp_dir,
                'images',
                'all_met_images.json'
            ),
            'w'
        ) as tmp_file:
            json.dump(data, tmp_file, ensure_ascii=False)

    def load_object_images_from_json_cache(self):
        """Load object images from JSON cache (single file).

        This JSON cache possibly contains the link between locally
        stored images and original JSON.

        :return:
        """
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'images', 'all_met_images.json')
        ):
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
                return data


def fetch_api_data_defaults(offset=0):
    """Fetch API data using defaults.

    :return:
    """
    client = MetropolitanClient()
    client.configure_from_settings()
    return client.get_object_list(offset=offset)
