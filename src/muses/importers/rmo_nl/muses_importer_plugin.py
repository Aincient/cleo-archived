from bs4 import BeautifulSoup

import requests
from six.moves.urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from ...base import BaseImporter, importer_registry

__all__ = (
    'NationalMuseumOfAntiquitiesImporter',
)

TIMEOUT = 10

ITEM_MAPPING = {
    'department_orig': 'Afdeling',
    'dimensions_orig': 'Afmetingenlabel',
    'description_orig': 'Beschrijving',
    'city_orig': 'City',
    'country_orig': 'GeoString',  # First element
    'inventory_number': 'Inventarisnummer',
    'material_orig': 'Materiaal',
    'object_type_orig': 'Objectnaam',
    'period_orig': 'Periode',
    'record_number': 'recordnumber',
    'title_orig': 'Titel',
    'acquired_orig': 'Vindplaats',
    'references_orig': 'Literatuur',
    'api_url': 'europeana_isShownAt',
    'site_found_orig': 'dc_identifier',
    'object_date_begin_orig': 'datebegin',
    'object_date_end_orig': 'dateend',
}


class NationalMuseumOfAntiquitiesImporter(BaseImporter):
    """National Museum of Antiquities (rmo.nl) importer."""

    uid = 'rmo_nl'
    name = 'rmo_nl'
    api_language = 'nl'

    def do_import(self):
        """Importer.

        :return:
        """
        url = self.config['url']
        response = requests.get(url)
        instances = []
        if response.ok:
            raw_data = response.text.encode('utf-8')
            xml_data = BeautifulSoup(raw_data, 'lxml-xml')
            items = xml_data.find_all('RMO_XML')
            # data = []
            for item in items:
                # data.append(self._extract_data(item))
                item_data = self._extract_item_data(item)
                item_instance = self.save_item(item_data)
                if item_instance:
                    images_data = self._extract_images_data(item)
                    self.save_images(item_instance, images_data)
                    instances.append(item_instance)
            return instances
        return []

    def _extract_item_data(self, item):
        """Extract photo data.

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
                item_data.update({key: getattr(item, value).text})
            except Exception as err:
                pass

        return item_data

    def _extract_images_data(self, item):
        """Extract images data.

        :param item:
        :type item:
        :return:
        :rtype list:
        """
        images_data = []
        base_image_url = item.europeana_isShownBy.text
        parsed_base_image_url = urlparse(base_image_url)
        query = parse_qs(parsed_base_image_url.query)
        query.pop('maxwidth', None)

        images = item.find_all('image')
        for image in images:
            query['filename'] = image.text
            parsed_image_url = parsed_base_image_url._replace(
                query=urlencode(query, True)
            )
            image_url = urlunparse(parsed_image_url)
            images_data.append({'api_url': image_url})

        return images_data


importer_registry.register(NationalMuseumOfAntiquitiesImporter)
