import json
import glob
import os

from django.conf import settings

import requests

from six import PY3
from six.moves import urllib
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import urljoin

from .conf import MUSES_IMPORTERS_THEWALTERS_ORG_IMAGES_BASE_PATH

__all__ = (
    'extract_filename_from_url',
    'fetch_api_data_defaults',
    'save_image',
    'TheWaltersClient',
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
        MUSES_IMPORTERS_THEWALTERS_ORG_IMAGES_BASE_PATH,
        basename
    )
    if PY3:
        urllib.request.urlretrieve(url, filename)
    else:
        urllib.urlretrieve(url, filename)
    return filename


class FatalError(Exception):
    """Fatal error."""


class TheWaltersClient(object):
    """Walters API client."""

    def __init__(self,
                 base_url=None,
                 api_key=None,
                 tmp_dir=None,
                 object_list_url=None,
                 object_detail_url=None,
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
        self._object_detail_url = object_detail_url
        self._geographical_location_list_url = geographical_location_list_url

    def configure_from_settings(self):
        """Configure from settings.

        :return:
        """
        config = settings.MUSES_CONFIG['importers']['thewalters_org']
        self.base_url = config['base_url']
        self.api_key = config['api_key']
        self.tmp_dir = config['tmp_dir']
        self._object_list_url = config['object_list_url']
        self._object_detail_url = config['object_detail_url']
        # self._object_images_url = config['object_images_url']
        # self._geographical_location_list_url = \
        #     config['geographical_location_list_url']

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
    def object_detail_url(self):
        """Get object detail URL.

        :return:
        :rtype: str
        """
        return urljoin(self.base_url, self._object_detail_url)

    def get_object_list(self, page):
        """Fetch API objects and dump results into the JSON files.

        - Fetches objects list (starting from the given offset).
        - Stores the fetched objects locally in the directory specified.

        :param page:
        :return:
        """
        if not page:
            page = 0

        data = []

        base_url = self.object_list_url

        while True:
            if page:
                url = '{}&page={}&apikey={}'.format(
                    base_url,
                    page,
                    self.api_key
                )
            else:
                url = '{}&apikey={}'.format(
                    base_url[:],
                    self.api_key
                )
            response = requests.get(url, data={}, headers=self.auth_headers)

            # Sometimes we get this error instead of a proper error response.
            # On first occurrence, stop and do not continue.
            try:
                result = response.json()
            except Exception as err:
                return page

            # Next page
            if 'NextPage' not in result or result['NextPage'] is False:
                return page

            if 'Items' in result and result['Items']:
                data += result['Items']
                page += 1
                with open(
                    os.path.join(
                        self.tmp_dir,
                        'objects',
                        'walters{}.json'.format(page)
                    ),
                    'w'
                ) as tmp_file:
                    json.dump(result['Items'], tmp_file, ensure_ascii=False)
            else:
                return page

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
            filtered_objects.update({obj['ObjectID']: obj})

        return filtered_objects

    def load_objects_from_json_cache(self):
        """Load objects from JSON cache.

        :return:
        """
        objects = []
        for filename in glob.glob(
            os.path.join(self.tmp_dir, 'objects', 'walters*.json')
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
            os.path.join(self.tmp_dir, 'objects', 'walters*.json')
        ):
            with open(filename, 'r') as json_file:
                json_data = json.load(json_file)
                for rec in json_data:
                    ids.add(rec['ObjectID'])
        return ids

    def get_object_images(self, obj):
        """Get object image.

        :param obj: JSON data.
        :type obj: dict
        :return:
        """
        data = []

        primary_image = obj['PrimaryImage']['Raw']

        for image in obj['Images'].split(','):
            _image = image.strip()
            img_url = 'http://static.thewalters.org/images/{}'.format(_image)

            if not img_url.startswith('http'):
                img_url = 'https://' + img_url

            is_primary_image = False
            if primary_image is not None:
                if _image in primary_image:
                    is_primary_image = True

            data.append(
                {'api_url': img_url, 'primary': is_primary_image}
            )

        return data

    def get_object_geographical_location(self,
                                         object_id,
                                         geographical_location_id=None):
        """Fetch API geo-location and dump results into the JSON files.

        - Fetches geographical-location list (starting from the given offset).
        - Stores the fetched geographical-location locally in the directory
          specified.

        :param object_id:
        :param geographical_location_id:
        :return:
        """
        base_url = self.object_detail_url[:]

        if object_id:
            url = base_url.format(object_id)
        else:
            url = base_url[:]

        url = '{}?apikey={}'.format(url, self.api_key)

        response = requests.get(url, data={}, headers=self.auth_headers)

        result = response.json()

        if 'Data' in result and result['Data']:
            if geographical_location_id is None:
                try:
                    geographical_location_id = \
                        result['Data']['Geographies'][0]['GeographyID']
                except Exception as err:
                    pass
            if geographical_location_id is not None:
                with open(
                    os.path.join(
                        self.tmp_dir,
                        'geo_locations',
                        'geo_location{}.json'.format(geographical_location_id)
                    ),
                    'w'
                ) as tmp_file:
                    json.dump(
                        result['Data']['Geographies'][0],
                        tmp_file,
                        ensure_ascii=False
                    )
                return result['Data']['Geographies'][0]

    def load_geographical_locations_from_json_cache(self):
        """Get geographical locations from JSON cache.

        :return:
        """
        objects = {}
        for filename in glob.glob(
                os.path.join(
                    self.tmp_dir,
                    'geo_locations',
                    'geo_location*.json'
                )
        ):
            with open(filename, 'r') as json_file:
                json_data = json.load(json_file)
                objects.update({json_data['GeographyID']: json_data})
        return objects


def fetch_api_data_defaults(page=0):
    """Fetch API data using defaults.

    :return:
    """
    client = TheWaltersClient()
    client.configure_from_settings()
    return client.get_object_list(page=page)
