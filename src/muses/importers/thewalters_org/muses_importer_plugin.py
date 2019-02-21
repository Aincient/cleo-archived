from six.moves.urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from ...base import BaseImporter, importer_registry
from .helpers import TheWaltersClient

__all__ = (
    'TheWaltersMuseumImporter',
)

TIMEOUT = 10

ITEM_MAPPING = {
    'department_orig': 'Collection',
    'dimensions_orig': 'Dimensions',
    'dynasty_orig': 'Dynasty',
    'description_orig': 'Description',
    # 'city_orig': '',  # City data is extracted in the code
    # 'country_orig': '',  # Country data is extracted in the code
    'inventory_number': 'ObjectNumber',
    'material_orig': 'Medium',
    'object_date_orig': 'DateText',
    'object_date_begin_orig': 'DateBeginYear',
    'object_date_end_orig': 'DateEndYear',
    'object_type_orig': 'ObjectName',
    'classification_orig': 'Classification',
    'period_orig': 'Period',
    'record_number': 'ObjectID',
    'title_orig': 'Title',
    'reign_orig': 'Reign',
    'keywords_orig': 'Keywords',
    # 'acquired_orig': '',  # No such information
    # 'references': '',  # No such information
    'api_url': 'ResourceURL',  # No such information
    # 'site_found_orig': '',  # No such information

    # New fields
    'museum_collection_orig': 'Collection',
    'style_orig': 'Style',
    'culture_orig': 'Culture',
    'inscriptions_orig': 'Inscriptions',
    'credit_line_orig': 'CreditLine',
    'provenance_orig': 'Provenance'
}


class TheWaltersMuseumImporter(BaseImporter):
    """The Walters Museum (thewalters.org) importer."""

    uid = 'thewalters_org'
    name = 'thewalters_org'
    api_language = 'en'

    def __init__(self, *args, **kwargs):
        self.client = TheWaltersClient()
        self.client_data = {}
        super(TheWaltersMuseumImporter, self).__init__(*args, **kwargs)

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
            refetch_geo = bool(int(self.options['refetch_geo']))
        except Exception as err:
            pass

        if refetch_objects:
            self.client.get_object_list(page=0)

        # Get all objects from cache (it's assumed, that the cache is
        # already built using
        # `./manage.py muses_thewalters_import --action objects` command
        objects = self.client.load_objects_from_json_cache()
        # _images = self.client.load_object_list_images_from_json_cache()
        # images = self.client.group_images_list_by_parent_object(_images)
        geo_locations = \
            self.client.load_geographical_locations_from_json_cache()

        egyptian_objects = self.client.filter_objects(objects)

        instances = []

        for object_id, object_data in egyptian_objects.items():
            item_data = self._extract_item_data(object_data, geo_locations)
            item_geo_ids = []
            if object_data['GeoIDs']:
                item_geo_ids = [
                    int(_id.strip())
                    for _id in object_data['GeoIDs'].split(',')
                    if object_data['GeoIDs']
                ]

            if refetch_geo:
                for item_geo_id in item_geo_ids:
                    item_geo_data = self.client.get_object_geographical_location(
                        object_id=item_data['ObjectID'],
                        geographical_location_id=item_geo_id
                    )
                    if item_geo_data is not None \
                            and item_geo_data['GeoType'] == 'Place of Origin':
                        if item_geo_data['GeographyID'] not in geo_locations:
                            geo_locations.update(
                                {item_geo_data['GeographyID']: item_geo_data}
                            )

            for item_geo_id in item_geo_ids:
                if item_geo_id in geo_locations:
                    if geo_locations[item_geo_id]['GeoType'] \
                            == 'Place of Origin':
                        item_data['geo_location'] = "POINT ({} {})".format(
                                geo_locations[item_geo_id]['LatitudeNumber'],
                                geo_locations[item_geo_id]['LongitudeNumber']
                            )
                        item_data['city_orig'] = \
                            geo_locations[item_geo_id]['GeographyTerm']

            item_instance = self.save_item(item_data)

            if item_instance:
                images_data = self._extract_images_data(object_data)
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
            refetch_geo = bool(int(self.options['refetch_geo']))
        except Exception as err:
            pass

        if refetch_objects:
            self.client.get_object_list(page=0)

        # Get all objects from cache (it's assumed, that the cache is
        # already built using
        # `./manage.py muses_thewalters_import --action objects` command
        objects = self.client.load_objects_from_json_cache()
        # _images = self.client.load_object_list_images_from_json_cache()
        # images = self.client.group_images_list_by_parent_object(_images)
        geo_locations = \
            self.client.load_geographical_locations_from_json_cache()

        egyptian_objects = self.client.filter_objects(objects)

        instances = []

        for object_id, object_data in egyptian_objects.items():
            item_data = self._extract_item_data(object_data, geo_locations)
            item_geo_ids = []
            if object_data['GeoIDs']:
                item_geo_ids = [
                    int(_id.strip())
                    for _id in object_data['GeoIDs'].split(',')
                    if object_data['GeoIDs']
                ]

            if refetch_geo:
                for item_geo_id in item_geo_ids:
                    item_geo_data = self.client.get_object_geographical_location(
                        object_id=item_data['ObjectID'],
                        geographical_location_id=item_geo_id
                    )
                    if item_geo_data is not None \
                            and item_geo_data['GeoType']== 'Place of Origin':
                        if item_geo_data['GeographyID'] not in geo_locations:
                            geo_locations.update(
                                {item_geo_data['GeographyID']: item_geo_data}
                            )

            for item_geo_id in item_geo_ids:
                if item_geo_id in geo_locations:
                    if geo_locations[item_geo_id]['GeoType'] \
                            == 'Place of Origin':
                        item_data['geo_location'] = "POINT ({} {})".format(
                                geo_locations[item_geo_id]['LatitudeNumber'],
                                geo_locations[item_geo_id]['LongitudeNumber']
                            )
                        item_data['city_orig'] = \
                            geo_locations[item_geo_id]['GeographyTerm']

            item_instance = self.get_item(item_data)

            if item_instance:
                for field in fields:
                    field_value = item_data.get(field)
                    if field_value is not None:
                        setattr(item_instance, field, field_value)
                item_instance.save()
                # images_data = self._extract_images_data(object_data)
                # self.save_images(item_instance, images_data)
                instances.append(item_instance)

        return instances

    # def _extract_geo_data(self, item, geo_data):
    #     """Extract geo data.
    #
    #     :param item:
    #     :return:
    #     """
    #     data = {}
    #     if item['geographical_locations']:
    #         loc = item['geographical_locations'][0]
    #         loc_id = loc['id']
    #         if loc_id in geo_data:
    #             if geo_data[loc_id]['city']:
    #                 data.update(
    #                     {'city_orig': geo_data[loc_id]['city']}
    #                 )
    #             if geo_data[loc_id]['country']:
    #                 data.update(
    #                     {'country_orig': geo_data[loc_id]['country']}
    #                 )
    #     return data

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

        # # Extract geo data.
        # item_data.update(self._extract_geo_data(item, geo_data))

        return item_data

    def _extract_images_data(self, item):
        """Extract images data.

        :param item:
        :param images: dict
        :type item:
        :type images: dict
        :return:
        :rtype list:
        """
        return self.client.get_object_images(item)


importer_registry.register(TheWaltersMuseumImporter)
