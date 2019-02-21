from collections import defaultdict
import json
import glob
import os

from django.conf import settings

import requests

from six import PY3
from six.moves import urllib
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import urljoin

from .conf import MUSES_IMPORTERS_BROOKLYNMUSEUM_ORG_IMAGES_BASE_PATH

__all__ = (
    'BrooklynClient',
    'extract_filename_from_url',
    'fetch_api_data_defaults',
    'save_image',
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
        MUSES_IMPORTERS_BROOKLYNMUSEUM_ORG_IMAGES_BASE_PATH,
        basename
    )
    if PY3:
        urllib.request.urlretrieve(url, filename)
    else:
        urllib.urlretrieve(url, filename)
    return filename


class FatalError(Exception):
    """Fatal error."""


class BrooklynClient(object):
    """Brooklyn API client."""

    def __init__(self,
                 base_url=None,
                 api_key=None,
                 tmp_dir=None,
                 object_list_url=None,
                 object_images_url=None,
                 geographical_location_list_url=None):
        """Constructor.

        :param base_url: Search URL.
        :param api_key: API key.
        :param tmp_dir: Temporary directory to store JSON files.
        :type base_url: str
        :type api_key: str
        :type tmp_dir: str
        """
        self.base_url = base_url
        self.api_key = api_key
        self.tmp_dir = tmp_dir
        self._object_list_url = object_list_url
        self._object_images_url = object_images_url
        self._geographical_location_list_url = geographical_location_list_url

    def configure_from_settings(self):
        """Configure from settings.

        :return:
        """
        config = settings.MUSES_CONFIG['importers']['brooklynmuseum_org']
        self.base_url = config['base_url']
        self.api_key = config['api_key']
        self.tmp_dir = config['tmp_dir']
        self._object_list_url = config['object_list_url']
        self._object_images_url = config['object_images_url']
        self._geographical_location_list_url = \
            config['geographical_location_list_url']

    def load_json_cache(self):
        """Load JSON cache.

        :return:
        """

    @property
    def auth_headers(self):
        """Auth headers.

        :return:
        """
        return {'api_key': self.api_key}

    @property
    def object_list_url(self):
        """Get object list URL.

        :return:
        :rtype: str
        """
        return urljoin(self.base_url, self._object_list_url)

    @property
    def object_images_url(self):
        """Get object images list URL.

        :return:
        :rtype: str
        """
        return urljoin(self.base_url, self._object_images_url)

    @property
    def geographical_location_list_url(self):
        """Get geographical-location list URL.

        :return:
        :rtype: str
        """
        return urljoin(self.base_url, self._geographical_location_list_url)

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

        base_url = self.object_list_url

        while True:
            if offset:
                url = '{}&offset={}'.format(base_url, offset)
            else:
                url = base_url[:]
            response = requests.get(url, data={}, headers=self.auth_headers)

            # Sometimes we get this error instead of a proper error response.
            # On first occurrence, stop and do not continue.
            if 'Fatal error' in response.text:
                return offset

            result = response.json()
            if 'data' in result and result['data']:
                data += result['data']

                # TODO, can it be that we should be increasing the value with
                # 35 (default limit) instead of just 1?
                offset += 1
                with open(
                    os.path.join(
                        self.tmp_dir,
                        'objects',
                        'brooklyn{}.json'.format(offset)
                    ),
                    'w'
                ) as tmp_file:
                    json.dump(result['data'], tmp_file, ensure_ascii=False)
            else:
                return offset

    def filter_objects_by_folder_value(self, objects, folder_value='egyptian'):
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
            if obj['collections']:
                found = False
                for col in obj['collections']:
                    # We only need objects with specified folder_value set.
                    if col['id'] == 5 and col['folder'] == folder_value:
                        found = True
                if found:
                    filtered_objects.update({obj['id']: obj})

        return filtered_objects

    def load_objects_from_json_cache(self):
        """Load objects from JSON cache.

        :return:
        """
        objects = []
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'objects', 'brooklyn*.json')
        ):
            with open(filename, 'r') as json_file:
                json_data = json.load(json_file)
                objects += json_data
        return objects

    def load_object_ids_from_json_cache(self):
        """Load object IDs from JSON cache.

        :return:
        """
        ids = set([])
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'objects', 'brooklyn*.json')
        ):
            with open(filename, 'r') as json_file:
                json_data = json.load(json_file)
                for rec in json_data:
                    ids.add(rec['id'])
        return ids

    def get_object_image(self, object_id):
        """Get object image.

        :param object_id: ID of the object for which we try to retrieve the
                          image.
        :type object_id: int
        :return:
        """
        data = []

        url = self.object_images_url.format(object_id)
        response = requests.get(url, data={}, headers=self.auth_headers)

        # Sometimes we get this error instead of a proper error response.
        # On first occurrence, stop and do not continue.
        if 'Fatal error' in response.text:
            return response.text

        result = response.json()

        if 'data' in result and result['data']:
            data += result['data']
            with open(
                os.path.join(
                    self.tmp_dir,
                    'images',
                    'brooklyn_images{}.json'.format(object_id)
                ),
                'w'
            ) as tmp_file:
                json.dump(result['data'], tmp_file, ensure_ascii=False)

    def get_object_list_images(self, object_ids):
        """Get all images for the given object list.

        :param object_ids: List of object IDs.
        :type object_ids: int
        :return:
        """
        errors = []
        for object_id in object_ids:
            err = self.get_object_image(object_id)
            if err:
                errors.append(object_id)
        return errors

    def get_object_list_images_from_json_cache(self):
        """Get all images for objects stored in cache.

        Note, that in this case images are not yet stored in the cache.
        We're using the objects from cache using
        :meth:`load_object_ids_from_json_cache`.

        :return:
        """
        object_ids = self.load_object_ids_from_json_cache()
        return self.get_object_list_images(object_ids)

    def group_images_list_by_parent_object(self, images):
        """Group images list by parent objects.

        :param images:
        :type images:
        :return:
        :rtype: dict
        """
        grouped_images = defaultdict(list)
        for img in images:
            grouped_images[img['object_id']].append(img)
        return grouped_images

    def load_object_list_images_from_json_cache(self):
        """Load images stored in JSON cache.

        :return:
        """
        objects = []
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'images', 'brooklyn_images*.json')
        ):
            with open(filename, 'r') as json_file:
                json_data = json.load(json_file)
                objects += json_data
        return objects

    def get_geographical_location_list(self, offset):
        """Fetch API geo-location and dump results into the JSON files.

        - Fetches geographical-location list (starting from the given offset).
        - Stores the fetched geographical-location locally in the directory
          specified.

        :param offset:
        :return:
        """
        if not offset:
            offset = 0

        data = []

        base_url = self.geographical_location_list_url

        while True:
            if offset:
                url = '{}&offset={}'.format(base_url, offset)
            else:
                url = base_url[:]
            response = requests.get(url, data={}, headers=self.auth_headers)

            # Sometimes we get this error instead of a proper error response.
            # On first occurrence, stop and do not continue.
            if 'Fatal error' in response.text:
                return offset

            result = response.json()
            if 'data' in result and result['data']:
                data += result['data']
                offset += 1
                with open(
                    os.path.join(
                        self.tmp_dir,
                        'geo_locations',
                        'geo_location{}.json'.format(offset)
                    ),
                    'w'
                ) as tmp_file:
                    json.dump(result['data'], tmp_file, ensure_ascii=False)
            else:
                return offset

    def load_geographical_locations_from_json_cache(self):
        """Get geographical locations from JSON cache.

        :return:
        """
        objects = []
        for filename in glob.glob(
                os.path.join(
                    self.tmp_dir,
                    'geo_locations',
                    'geo_location*.json'
                )
        ):
            with open(filename, 'r') as json_file:
                json_data = json.load(json_file)
                objects += json_data
        return objects


def fetch_api_data_defaults(offset=0):
    """Fetch API data using defaults.

    :return:
    """
    client = BrooklynClient()
    client.configure_from_settings()
    return client.get_object_list(offset=offset)
