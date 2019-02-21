from six.moves.urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from ...base import BaseImporter, importer_registry
from .helpers import MetropolitanClient

__all__ = (
    'MetropolitanMuseumImporter',
)

TIMEOUT = 10

ITEM_MAPPING = {
    'department_orig': 'Department',  # Done
    'dimensions_orig': 'Dimensions',  # Done
    'dynasty_orig': 'Dynasty',  # Done
    'description_orig': 'Locus',  # Done
    'city_orig': 'City',  # Done
    'country_orig': 'Country',  # Done
    'inventory_number': 'Object Number',  # Done
    'material_orig': 'Medium',  # Done
    'object_date_orig': 'Object Date',  # Done
    'object_date_begin_orig': 'Object Begin Date',  # Done
    'object_date_end_orig': 'Object End Date',  # Done
    'object_type_orig': 'Classification',  # Done
    'classification_orig': 'Object Name',  # Done
    'period_orig': 'Period',  # Done
    'record_number': 'Object ID',  # Done
    'title_orig': 'Title',  # Done
    'reign_orig': 'Reign',  # Done
    # 'keywords_orig': 'Locus',  # No such information
    # 'acquired_orig': '',  # No such information
    # 'references': '',  # No such information
    'api_url': 'Link Resource',  # Done
    # 'site_found_orig': '',  # No such information

    # New fields
    'credit_line_orig': 'Credit Line',
    'region_orig': 'Region',
    'sub_region_orig': 'Subregion',
    'locale_orig': 'Locale',
    'excavation_orig': 'Excavation',
}


class MetropolitanMuseumImporter(BaseImporter):
    """Metropolitan Museum (metmuseum.org) importer."""

    uid = 'metmuseum_org'
    name = 'metmuseum_org'
    api_language = 'en'

    def __init__(self, *args, **kwargs):
        self.client = MetropolitanClient()
        self.client_data = {}
        super(MetropolitanMuseumImporter, self).__init__(*args, **kwargs)

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

        try:
            refetch_objects = bool(int(self.options['refetch_objects']))
        except Exception as err:
            pass

        try:
            refetch_images = bool(int(self.options['refetch_images']))
        except Exception as err:
            pass

        if refetch_objects:
            objects = self.client.get_object_list(offset=0)

        if refetch_images:
            self.client.get_object_list_images_from_json_cache()

        # Get all objects from cache (it's assumed, that the cache is
        # already built using
        # `./manage.py muses_brooklyn_import --action objects` command
        objects = self.client.load_objects_from_json_cache()
        images = self.client.load_object_list_images_from_json_cache()

        instances = []

        for object_id, object_data in objects.items():
            item_data = self._extract_item_data(object_data)
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

        try:
            refetch_objects = bool(int(self.options['refetch_objects']))
        except Exception as err:
            pass

        try:
            refetch_images = bool(int(self.options['refetch_images']))
        except Exception as err:
            pass

        if refetch_objects:
            self.client.get_object_list(offset=0)

        if refetch_images:
            self.client.get_object_list_images_from_json_cache()

        # Get all objects from cache (it's assumed, that the cache is
        # already built using
        # `./manage.py muses_brooklyn_import --action objects` command
        objects = self.client.load_objects_from_json_cache()
        images = self.client.load_object_list_images_from_json_cache()

        instances = []

        for object_id, object_data in objects.items():
            item_data = self._extract_item_data(object_data)
            item_instance = self.get_item(item_data)
            if item_instance:
                # images_data = self._extract_images_data(object_data, images)
                # self.save_images(item_instance, images_data)
                for field in fields:
                    field_value = item_data.get(field)
                    if field_value is not None:
                        setattr(item_instance, field, field_value)
                item_instance.save()
                instances.append(item_instance)

        return instances

    def _extract_item_data(self, item):
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
        object_id = item['Object ID']
        if object_id in images:
            for counter, image in enumerate(images[object_id]):
                img_url = image['originalImageUrl']
                if not img_url.startswith('http'):
                    img_url = 'https://' + img_url
                images_data.append(
                    {
                        'api_url': img_url,
                        'primary': counter == 0,  # First image is primary
                    }
                )

        return images_data


importer_registry.register(MetropolitanMuseumImporter)
