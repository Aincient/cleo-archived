from six.moves.urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from ...base import BaseImporter, importer_registry
from .helpers import BrooklynClient

__all__ = (
    'BrooklynMuseumImporter',
)

TIMEOUT = 10

ITEM_MAPPING = {
    # 'department_orig': 'Afdeling',
    'dimensions_orig': 'dimensions',
    'dynasty_orig': 'dynasty',
    'description_orig': 'description',
    # 'city_orig': '',  # City data is extracted in the code
    # 'country_orig': '',  # Country data is extracted in the code
    'inventory_number': 'accession_number',
    'material_orig': 'medium',
    'object_date_orig': 'object_date',
    'object_date_begin_orig': 'object_date_begin',
    'object_date_end_orig': 'object_date_end',
    'object_type_orig': 'classification',
    'period_orig': 'period',
    'record_number': 'id',
    'title_orig': 'title',
    # 'acquired_orig': '',  # No such information
    # 'references': '',  # No such information
    # 'api_url': '',  # No such information
    # 'site_found_orig': '',  # No such information

    # New fields
    'accession_date': 'accession_date',
    'inscriptions_orig': 'inscribed',
    'credit_line_orig': 'credit_line',
    # Exhibitions are handled in the code
}


class BrooklynMuseumImporter(BaseImporter):
    """Brooklyn Museum (brooklynmuseum.org) importer."""

    uid = 'brooklynmuseum_org'
    name = 'brooklynmuseum_org'
    api_language = 'en'

    def __init__(self, *args, **kwargs):
        self.client = BrooklynClient()
        self.client_data = {}
        super(BrooklynMuseumImporter, self).__init__(*args, **kwargs)

    def setup(self):
        """Set up.

        :return:
        """
        # Initialise API client
        self.client.configure_from_settings()

    def do_import(self):
        """Importer.

        :return:
        """
        refetch_objects = False
        refetch_images = False
        refetch_geo = False

        try:
            refetch_objects = bool(int(self.options['refetch_objects']))
        except Exception as err:
            pass

        try:
            refetch_images = bool(int(self.options['refetch_images']))
        except Exception as err:
            pass

        try:
            refetch_geo = bool(int(self.options['refetch_geo']))
        except Exception as err:
            pass

        if refetch_objects:
            self.client.get_object_list(offset=0)

        if refetch_images:
            self.client.get_object_list_images_from_json_cache()

        if refetch_geo:
            self.get_geographical_location_list(offset=0)

        # Get all objects from cache (it's assumed, that the cache is
        # already built using
        # `./manage.py muses_brooklyn_import --action objects` command
        objects = self.client.load_objects_from_json_cache()
        _images = self.client.load_object_list_images_from_json_cache()
        images = self.client.group_images_list_by_parent_object(_images)

        egyptian_objects = self.client.filter_objects_by_folder_value(objects)

        geo_data = {}
        for item in self.client.load_geographical_locations_from_json_cache():
            geo_data.update({item['id']: item})

        instances = []

        for object_id, object_data in egyptian_objects.items():
            item_data = self._extract_item_data(object_data, geo_data)
            item_instance = self.save_item(item_data)
            if item_instance:
                images_data = self._extract_images_data(object_data, images)
                self.save_images(item_instance, images_data)
                instances.append(item_instance)

        return instances

    def do_update(self, fields):
        """Importer.

        :return:
        """
        refetch_objects = False
        refetch_images = False
        refetch_geo = False

        try:
            refetch_objects = bool(int(self.options['refetch_objects']))
        except Exception as err:
            pass

        try:
            refetch_images = bool(int(self.options['refetch_images']))
        except Exception as err:
            pass

        try:
            refetch_geo = bool(int(self.options['refetch_geo']))
        except Exception as err:
            pass

        if refetch_objects:
            self.client.get_object_list(offset=0)

        if refetch_images:
            self.client.get_object_list_images_from_json_cache()

        if refetch_geo:
            self.get_geographical_location_list(offset=0)

        # Get all objects from cache (it's assumed, that the cache is
        # already built using
        # `./manage.py muses_brooklyn_import --action objects` command
        objects = self.client.load_objects_from_json_cache()
        _images = self.client.load_object_list_images_from_json_cache()
        images = self.client.group_images_list_by_parent_object(_images)

        egyptian_objects = self.client.filter_objects_by_folder_value(objects)

        geo_data = {}
        for item in self.client.load_geographical_locations_from_json_cache():
            geo_data.update({item['id']: item})

        instances = []

        for object_id, object_data in egyptian_objects.items():
            item_data = self._extract_item_data(object_data, geo_data)
            item_instance = self.get_item(item_data)
            if item_instance:
                images_data = self._extract_images_data(object_data, images)
                self.save_images(item_instance, images_data)
                for field in fields:
                    field_value = item_data.get(field)
                    if field_value is not None:
                        setattr(item_instance, field, field_value)
                item_instance.save()
                instances.append(item_instance)

        return instances

    def _extract_geo_data(self, item, geo_data):
        """Extract geo data.

        :param item:
        :return:
        """
        data = {}
        if item['geographical_locations']:
            loc = item['geographical_locations'][0]
            loc_id = loc['id']
            if loc_id in geo_data:
                if geo_data[loc_id]['city']:
                    data.update(
                        {'city_orig': geo_data[loc_id]['city']}
                    )
                if geo_data[loc_id]['country']:
                    data.update(
                        {'country_orig': geo_data[loc_id]['country']}
                    )
        return data

    def _extract_exhibitions_data(self, item):
        """Extract exhibitions data.

        :param item:
        :return:
        """
        data = []
        if 'exhibitions' in item and item['exhibitions']:
            if isinstance(item['exhibitions'], (list, tuple)):
                for _ex in item['exhibitions']:
                    try:
                        data.append(_ex['title'])
                    except Exception as err:
                        pass

        return data

    def _extract_item_data(self, item, geo_data):
        """Extract item data.

        :param item:
        :type item:
        :return:
        :rtype dict:
        """
        item_data = {
            'importer_uid': self.uid,
            'language_code_orig': self.api_language,
        }

        for key, value in ITEM_MAPPING.items():
            try:
                item_data.update({key: item.get(value)})
            except Exception as err:
                pass

        item_data['api_url'] = 'https://www.brooklynmuseum.org/' \
                               'opencollection' \
                               '/objects/{}'.format(item_data['record_number'])

        # Extract geo data.
        item_data.update(self._extract_geo_data(item, geo_data))

        exhibitions_data = self._extract_exhibitions_data(item)
        if exhibitions_data:
            item_data.update({'exhibitions': exhibitions_data})

        return item_data

    def _extract_images_data(self, item, images):
        """Extract images data.

        :param item:
        :param images: dict
        :type item:
        :type images: dict
        :return:
        :rtype list:
        """
        images_data = []
        object_id = item['id']
        primary_image = item['primary_image']
        if object_id in images:
            for image in images[object_id]:
                is_primary_image = False
                img_url = image['largest_derivative_url']
                if primary_image == image['filename']:
                    is_primary_image = True
                if not img_url.startswith('http'):
                    img_url = 'https://' + img_url
                images_data.append(
                    {'api_url': img_url, 'primary': is_primary_image}
                )

        return images_data


importer_registry.register(BrooklynMuseumImporter)
